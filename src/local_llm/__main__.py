import asyncio

from viam.module.module import Module
from chat_service_api import Chat

from . import Llm


async def main():
    module = Module.from_args()
    module.add_model_from_registry(Chat.API, Llm.MODEL)
    await module.start()


asyncio.run(main())
