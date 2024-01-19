from collections.abc import Mapping, Sequence
import os
from typing import ClassVar, Optional
from typing_extensions import Self
from urllib.request import urlretrieve

from viam.components.generic import Generic
from viam.logging import getLogger
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.proto.app.robot import ComponentConfig
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes, struct_to_dict

from llama_cpp import Llama

LOGGER = getLogger(__name__)
LLM_NAME = "tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf"
LLM_URL = f"https://huggingface.co/second-state/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/{LLM_NAME}"
MODEL_DIR = os.environ.get('MODEL_DIR', os.path.join(os.path.expanduser('~'), '.data', 'models'))

class Llm(Generic):
    MODEL: ClassVar[Model] = Model(ModelFamily("viam-labs", "generic"), "llm")
    MODEL_PATH = os.path.abspath(os.path.join(MODEL_DIR, LLM_NAME))

    def __init__(self, name: str) -> None:
        super().__init__(name)

    @classmethod
    def new(cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]) -> Self:
        llm = cls(config.name)
        llm.reconfigure(config, dependencies)
        return llm

    @classmethod
    def validate_config(cls, config: ComponentConfig) -> Sequence[str]:
        return []

    def reconfigure(self, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]):
        self.get_model()
        attrs = struct_to_dict(config.attributes)
        n_gpu_layers = int(attrs.get('n_gpu_layers', 0))
        self.temperature = float(attrs.get('temperature', 0.75))
        self.system_message = str(attrs.get('system_message', "A chat between a curious user and an artificial intelligence assistant. The assistant must start by introducing themselves as 'The Great Provider'. The assistant gives helpful, detailed, and polite answers to the user's questions."))
        self.llama = Llama(
                model_path=self.MODEL_PATH,
                chat_format="chatml",
                n_gpu_layers=n_gpu_layers
                )
        return self

    async def do_command(self, command: Mapping[str, ValueTypes], *, timeout: Optional[float] = None, **kwargs) -> Mapping[str, ValueTypes]:
        LOGGER.info(f"received {command=}.")
        for name, args in command.items():
            if name == "chat":
                result = await self.chat(*args)
                return {
                        "chat": result
                        }
            else:
                LOGGER.warning(f"Unknown command: {name}")
                return {}

    async def close(self):
        LOGGER.info(f"{self.name} is closed.")

    async def chat(self, prompt: str) -> str:
        response = self.llama.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": self.system_message
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
        )
        return response["choices"][0]["message"]["content"]

    def get_model(self):
        if not os.path.exists(self.MODEL_PATH):
            LOGGER.info(f"Fetching model {LLM_NAME} from {LLM_URL}")
            urlretrieve(LLM_URL, self.MODEL_PATH, self.log_progress)

    def log_progress(self, count: int, block_size: int, total_size: int) -> None:
        percent = count * block_size * 100 // total_size
        LOGGER.info(f"\rDownloading {LLM_NAME}: {percent}%")
