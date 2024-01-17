from collections.abc import Mapping, Sequence
import os
from typing import ClassVar, Optional, Self
from urllib.request import urlretrieve

from viam.components.generic import Generic
from viam.logging import getLogger
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.proto.app.robot import ComponentConfig
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes

from llama_cpp import Llama

LOGGER = getLogger(__name__)
LLM_NAME = "tinyllama-1.1B-chat-v1.0.Q5_K_M.gguf"
LLM_URL = f"https://huggingface.co/second-state/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/{LLM_NAME}"
SYSTEM_MESSAGE = {
        "role": "system",
        "content": "A chat between a curious user and an artificial intelligence assistant. The assistant must start by introducing themselves as 'The Great Provider'. The assistant gives helpful, detailed, and polite answers to the user's questions."
        }

class Llm(Generic):
    MODEL: ClassVar[Model] = Model(ModelFamily("viam-labs", "generic"), "llm")

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
        self.llama = Llama(
                model_path=os.path.abspath(os.path.join(os.path.expanduser('~'), '.viam', 'models', LLM_NAME)),
                chat_format="llama-2"
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
                    SYSTEM_MESSAGE,
                    {
                        "role": "user",
                        "content": prompt
                        }
                    ]
                )
        return response[0]["text"]

    def get_model(self):
        if not os.path.exists(os.path.abspath(os.path.join(os.path.expanduser('~'), '.viam', 'models', LLM_NAME))):
            urlretrieve(LLM_URL, LLM_NAME, self.log_progress)

    def log_progress(self, count: int, block_size: int, total_size: int) -> None:
        percent = count * block_size * 100 // total_size
        LOGGER.info(f"\rDownloading {LLM_NAME}: {percent}%")
