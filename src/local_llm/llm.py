import asyncio
from collections.abc import Mapping, Sequence
from typing import ClassVar, Optional, Self

from viam.components.generic import Generic
from viam.logging import getLogger
from viam.proto.common import ResourceName
from viam.resource.base import ResourceBase
from viam.proto.app.robot import ComponentConfig
from viam.resource.types import Model, ModelFamily
from viam.utils import ValueTypes

LOGGER = getLogger(__name__)


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
        return self

    async def do_command(self, command: Mapping[str, ValueTypes], *, timeout: Optional[float] = None, **kwargs) -> Mapping[str, ValueTypes]:
        LOGGER.info(f"received {command=}.")
        return command

    async def close(self):
        LOGGER.info(f"{self.name} is closed.")
