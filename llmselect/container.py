from dataclasses import dataclass

from .services.comparisons import ComparisonService
from .services.conversations import ConversationService
from .services.llm import LLMService
from .services.model_registry import ModelRegistryService


@dataclass
class ServiceContainer:
    llm: LLMService
    conversations: ConversationService
    comparisons: ComparisonService
    model_registry: ModelRegistryService


def create_service_container(app=None) -> ServiceContainer:
    max_tokens = 1000
    use_azure = False
    azure_endpoint = None
    azure_api_key = None
    azure_api_version = None
    azure_deployment_mappings = {}

    if app and hasattr(app.config, "get"):
        max_tokens = app.config.get("LLM_MAX_TOKENS", 1000)
        use_azure = app.config.get("USE_AZURE_FOUNDRY", False)
        azure_endpoint = app.config.get("AZURE_AI_FOUNDRY_ENDPOINT")
        azure_api_key = app.config.get("AZURE_AI_FOUNDRY_KEY")
        azure_api_version = app.config.get("AZURE_AI_FOUNDRY_API_VERSION")
        azure_deployment_mappings = app.config.get("AZURE_DEPLOYMENT_MAPPINGS", {})

    return ServiceContainer(
        llm=LLMService(
            max_tokens=max_tokens,
            use_azure=use_azure,
            azure_endpoint=azure_endpoint,
            azure_api_key=azure_api_key,
            azure_api_version=azure_api_version,
            azure_deployment_mappings=azure_deployment_mappings,
        ),
        conversations=ConversationService(),
        comparisons=ComparisonService(),
        model_registry=ModelRegistryService(),
    )
