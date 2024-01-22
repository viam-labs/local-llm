import asyncio

from viam.robot.client import RobotClient
from viam.logging import getLogger

from chat_service_api import Chat

LOGGER = getLogger(__name__)

async def connect():
    opts = RobotClient.Options.with_api_key(
	  # Replace "<API-KEY>" (including brackets) with your machine's api key
      api_key='<API-KEY>',
	  # Replace "<API-KEY-ID>" (including brackets) with your machine's api key id
      api_key_id='<API-KEY-ID>'
    )
    return await RobotClient.at_address('<ADDRESS>', opts)

async def main():
    robot = await connect()

    print('Resources:')
    print(robot.resource_names)

    llm = Chat.from_robot(robot, name="llm")

    prompt = "Please provide a list of famous robots from history."
    response =  await llm.chat(prompt)
    print(f"Prompt: {prompt}")
    print(f"Answer: {response}")

    # Don't forget to close the machine when you're done!
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
