from chat_service_api import Chat
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .llm import Llm

Registry.register_resource_creator(
    Chat.API, Llm.MODEL, ResourceCreatorRegistration(Llm.new, Llm.validate_config)
)
