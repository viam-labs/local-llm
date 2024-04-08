import asyncio
from collections.abc import Mapping, Sequence
import os
from typing import ClassVar
from typing_extensions import Self
from urllib.request import urlretrieve

from viam.logging import getLogger
from viam.module.module import Reconfigurable
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.proto.app.robot import ComponentConfig
from viam.resource.types import Model, ModelFamily
from viam.utils import struct_to_dict

from chat_service_api import Chat
from llama_cpp import Llama

LOGGER = getLogger(__name__)
MODEL_DIR = os.environ.get(
    "VIAM_MODULE_DATA", os.path.join(os.path.expanduser("~"), ".data", "models")
)


class Llm(Chat, Reconfigurable):
    MODEL: ClassVar[Model] = Model(ModelFamily("viam-labs", "chat"), "llm")
    LLM_REPO = ""
    LLM_FILE = ""
    MODEL_PATH = os.path.abspath(os.path.join(MODEL_DIR, LLM_FILE))

    llama = None

    def __init__(self, name: str) -> None:
        super().__init__(name)

    @classmethod
    def new(
        cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ) -> Self:
        llm = cls(config.name)
        llm.reconfigure(config, dependencies)
        return llm

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        return []

    def reconfigure(
        self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
    ):
        attrs = struct_to_dict(config.attributes)
        LOGGER.info(attrs)
        self.LLM_REPO = str(
            attrs.get("llm_repo", "second-state/TinyLlama-1.1B-Chat-v1.0-GGUF")
        )
        self.LLM_FILE = str(
            attrs.get("llm_file", "tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf")
        )
        self.MODEL_PATH = os.path.abspath(os.path.join(MODEL_DIR, self.LLM_FILE))

        self.n_gpu_layers = int(attrs.get("n_gpu_layers", 0))
        self.temperature = float(attrs.get("temperature", 0.75))
        self.system_message = str(
            attrs.get(
                "system_message",
                "A chat between a curious user and an artificial intelligence assistant. The assistant must start by introducing themselves as 'The Great Provider'. The assistant gives helpful, detailed, and polite answers to the user's questions.",
            )
        )
        self.debug = bool(attrs.get("debug", False))
        asyncio.create_task(self._ensure_llama())

    async def close(self):
        LOGGER.info(f"{self.name} is closed.")

    async def chat(self, message: str) -> str:
        if self.llama is None:
            raise Exception("LLM is not ready")

        response = self.llama.create_chat_completion(
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": message},
            ],
            temperature=self.temperature,
        )
        return response["choices"][0]["message"]["content"]

    async def get_model(self):
        if not os.path.exists(self.MODEL_PATH):
            LLM_URL = (
                f"https://huggingface.co/{self.LLM_REPO}/resolve/main/{self.LLM_FILE}"
            )
            LOGGER.info(f"Fetching model {self.LLM_FILE} from {LLM_URL}")
            urlretrieve(LLM_URL, self.MODEL_PATH, self.log_progress)

    def log_progress(self, count: int, block_size: int, total_size: int) -> None:
        percent = count * block_size * 100 // total_size
        LOGGER.info(f"\rDownloading {self.LLM_FILE}: {percent}%")

    async def _ensure_llama(self):
        await self.get_model()

        self.llama = Llama(
            model_path=self.MODEL_PATH,
            chat_format="chatml",
            n_gpu_layers=self.n_gpu_layers,
            verbose=self.debug,
            logits_all=True,
        )
