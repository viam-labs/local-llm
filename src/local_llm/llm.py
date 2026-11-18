import asyncio
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Tuple
from urllib.request import urlretrieve

from chat_service_api import Chat
from llama_cpp import Llama
from typing_extensions import Self
from viam.logging import getLogger
from viam.module.types import Reconfigurable
from viam.proto.app.robot import ComponentConfig
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.resource.types import Model, ModelFamily
from viam.utils import struct_to_dict

LOGGER = getLogger(__name__)
MODEL_DIR = os.environ.get(
    "VIAM_MODULE_DATA", os.path.join(os.path.expanduser("~"), ".data", "models")
)

DEFAULT_SYSTEM_MESSAGE = "You are a helpful assistant. Answer clearly and concisely."


@dataclass(frozen=True)
class Settings:
    llm_repo: str = "second-state/TinyLlama-1.1B-Chat-v1.0-GGUF"
    llm_file: str = "tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf"
    n_gpu_layers: int = 0
    # Newer models declare contexts of 128k tokens or more, and llama.cpp reserves memory for the
    # whole context up front, so the default stays small.
    n_ctx: int = 2048
    # None uses the chat template stored in the model file.
    chat_format: Optional[str] = None
    temperature: float = 0.75
    system_message: str = DEFAULT_SYSTEM_MESSAGE
    # None: half the CPU cores, llama-cpp-python's default for generation.
    n_threads: Optional[int] = None
    debug: bool = False

    @classmethod
    def from_attributes(cls, attrs: Mapping[str, Any]) -> "Settings":
        if "llm_repo" in attrs and "llm_file" not in attrs:
            raise ValueError("llm_file must be set when llm_repo is set")
        n_threads = (
            int(attrs["n_threads"]) if attrs.get("n_threads") is not None else None
        )
        if n_threads is not None and n_threads < 1:
            raise ValueError("n_threads must be at least 1")
        d = cls()
        return cls(
            n_threads=n_threads,
            llm_repo=str(attrs.get("llm_repo", d.llm_repo)),
            llm_file=str(attrs.get("llm_file", d.llm_file)),
            n_gpu_layers=int(attrs.get("n_gpu_layers", d.n_gpu_layers)),
            n_ctx=int(attrs.get("n_ctx", d.n_ctx)),
            chat_format=str(attrs["chat_format"]) if attrs.get("chat_format") else None,
            temperature=float(attrs.get("temperature", d.temperature)),
            system_message=str(attrs.get("system_message", d.system_message)),
            debug=bool(attrs.get("debug", d.debug)),
        )

    @property
    def model_path(self) -> str:
        return os.path.abspath(os.path.join(MODEL_DIR, self.llm_file))

    @property
    def threads(self) -> int:
        return self.n_threads or max((os.cpu_count() or 2) // 2, 1)


class Llm(Chat, Reconfigurable):
    MODEL: ClassVar[Model] = Model(ModelFamily("viam-labs", "chat"), "llm")

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.settings = Settings()
        self.llama: Optional[Llama] = None
        self.load_error: Optional[Exception] = None
        self._load_task: Optional[asyncio.Task] = None
        # Llama is not thread-safe, so chats run one at a time.
        self._chat_lock = asyncio.Lock()

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        llm = cls(config.name)
        llm.reconfigure(config, dependencies)
        return llm

    @classmethod
    def validate_config(
        cls, config: ComponentConfig
    ) -> Tuple[Sequence[str], Sequence[str]]:
        Settings.from_attributes(struct_to_dict(config.attributes))
        # No required or optional dependencies.
        return [], []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        attrs = struct_to_dict(config.attributes)
        LOGGER.debug(attrs)
        self.settings = Settings.from_attributes(attrs)
        # A load still in progress belongs to the old settings: stop waiting for it, so it
        # can't replace the model loaded below.
        if self._load_task is not None:
            self._load_task.cancel()
        self.llama = None
        self.load_error = None
        self._load_task = asyncio.create_task(self._load(self.settings))

    async def close(self):
        if self._load_task is not None:
            self._load_task.cancel()
        LOGGER.info(f"{self.name} is closed.")

    async def chat(self, message: str) -> str:
        llama, settings = self.llama, self.settings
        if llama is None:
            if self.load_error is not None:
                raise Exception(f"LLM failed to load: {self.load_error}")
            raise Exception("LLM is not ready")

        # Generation takes seconds; run it off the event loop so the module keeps serving.
        async with self._chat_lock:
            response = await asyncio.to_thread(
                llama.create_chat_completion,
                messages=[
                    {"role": "system", "content": settings.system_message},
                    {"role": "user", "content": message},
                ],
                temperature=settings.temperature,
            )
        return response["choices"][0]["message"]["content"]

    async def _load(self, settings: Settings):
        try:
            await asyncio.to_thread(download_model, settings)
            llama = await asyncio.to_thread(
                Llama,
                model_path=settings.model_path,
                chat_format=settings.chat_format,
                n_gpu_layers=settings.n_gpu_layers,
                n_ctx=settings.n_ctx,
                # llama-cpp-python reads prompts with every core by default. When other work keeps
                # a core busy, the starved thread stalls the rest: on a 16-core robot running SLAM,
                # a 70-token prompt took 7-9 s instead of 0.5 s. Use the generation count for both.
                n_threads=settings.threads,
                n_threads_batch=settings.threads,
                verbose=settings.debug,
            )
        except asyncio.CancelledError:
            raise
        except Exception as e:
            LOGGER.error(f"Failed to load {settings.llm_file}: {e}")
            self.load_error = e
            return
        self.llama = llama
        LOGGER.info(f"{settings.llm_file} is loaded and ready")


def download_model(settings: Settings) -> None:
    path = settings.model_path
    if os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    url = f"https://huggingface.co/{settings.llm_repo}/resolve/main/{settings.llm_file}"
    LOGGER.info(f"Fetching model {settings.llm_file} from {url}")

    last_logged = -1

    def log_progress(count: int, block_size: int, total_size: int) -> None:
        nonlocal last_logged
        if total_size <= 0:
            return
        percent = min(100, count * block_size * 100 // total_size)
        if percent // 10 > last_logged // 10:
            last_logged = percent
            LOGGER.info(f"Downloading {settings.llm_file}: {percent}%")

    # Download beside the final path and rename when done, so an interrupted download is
    # retried on the next load instead of being taken for the model.
    partial = path + ".part"
    urlretrieve(url, partial, log_progress)
    os.replace(partial, path)
