import asyncio

from viam.robot.client import RobotClient
from viam.components.generic import Generic
from viam.logging import getLogger

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

    llm = Generic.from_robot(robot, name="llm")

    response =  await llm.do_command({ "chat": ["Please provide a list of famous robots from history."]})
    print(f"The machine replied with {response}")

    # Don't forget to close the machine when you're done!
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
