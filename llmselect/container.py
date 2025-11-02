from dataclasses import dataclass

from .services.comparisons import ComparisonService
from .services.conversations import ConversationService
from .services.llm import LLMService


@dataclass
class ServiceContainer:
    llm: LLMService
    conversations: ConversationService
    comparisons: ComparisonService


def create_service_container(app=None) -> ServiceContainer:
    max_tokens = 1000
    if app and hasattr(app.config, 'get'):
        max_tokens = app.config.get('LLM_MAX_TOKENS', 1000)
    
    return ServiceContainer(
        llm=LLMService(max_tokens=max_tokens),
        conversations=ConversationService(),
        comparisons=ComparisonService(),
    )
