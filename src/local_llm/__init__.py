from viam.components.generic import Generic
from viam.resource.registry import Registry, ResourceCreatorRegistration

from .llm import Llm

Registry.register_resource_creator(Generic.SUBTYPE, Llm.MODEL, ResourceCreatorRegistration(Llm.new, Llm.validate_config))
