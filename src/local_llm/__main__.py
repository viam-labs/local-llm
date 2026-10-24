import asyncio

from chat_service_api import Chat
from viam.module.module import Module

from . import Llm


async def main():
    module = Module.from_args()
    module.add_model_from_registry(Chat.API, Llm.MODEL)
    await module.start()


asyncio.run(main())
