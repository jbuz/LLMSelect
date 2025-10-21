from dataclasses import dataclass

from .services.conversations import ConversationService
from .services.llm import LLMService


@dataclass
class ServiceContainer:
    llm: LLMService
    conversations: ConversationService


def create_service_container() -> ServiceContainer:
    return ServiceContainer(llm=LLMService(), conversations=ConversationService())
