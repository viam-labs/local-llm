import asyncio

from viam.components.generic import Generic
from viam.module.module import Module

from . import Llm

async def main():
    module = Module.from_args()
    module.add_model_from_registry(Generic.SUBTYPE, Llm.MODEL)
    await module.start()

asyncio.run(main())
