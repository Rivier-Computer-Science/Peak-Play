# Example usage:
# gpt_41_llm = GPT4_1Config().create_llm()
# print(GPT4_1Config().get_options())
# print(GPT4_1Config().get_cost())

from abc import ABC, abstractmethod
from typing import Any, Dict
import crewai as crewai


class BaseLLMConfig(ABC):
    def __init__(
        self,
        model_name: str = 'gpt-4o',
        temperature: float = 0.7,
        max_tokens: int = 5000,
        presence_penalty: float = 0.5,
        num_retries: int = 3,
        timeout: int = 120,
        **kwargs: Any
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.presence_penalty = presence_penalty
        self.num_retries = num_retries
        self.timeout = timeout
        self.kwargs: Dict[str, Any] = dict(kwargs)

    def create_llm(self, **overrides: Any) -> crewai.LLM:
        """
        Return a crewai.LLM instance ready to use in agents.
        """
        # Resolve core fields (overrides win)
        model = overrides.pop("model", overrides.pop("model_name", self.model_name))
        provider = overrides.pop("provider", self.kwargs.get("provider", "openai"))
        temperature = overrides.pop("temperature", self.temperature)
        max_tokens = overrides.pop("max_tokens", self.max_tokens)
        presence_penalty = overrides.pop("presence_penalty", self.presence_penalty)
        num_retries = overrides.pop("num_retries", self.kwargs.get("num_retries", self.num_retries))
        timeout = overrides.pop("timeout", self.kwargs.get("timeout", self.timeout))

        # Merge extra kwargs (api_key, base_url, etc.)
        final_kwargs = {**self.kwargs, **overrides}
        # Normalize / drop keys LiteLLM doesn't use directly
        final_kwargs.pop("model_name", None)
        final_kwargs.pop("provider", None)

        # Build a provider-qualified model id (recommended by CrewAI/LiteLLM)
        model_id = model if "/" in model else f"{provider}/{model}"

        cfg: Dict[str, Any] = {
            "model": model_id,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "presence_penalty": presence_penalty,
            "num_retries": num_retries,
            "timeout": timeout,
            # tolerate unknown params across providers
            "drop_params": True,
            "additional_drop_params": ["model_name"],
            **final_kwargs,
        }
        return crewai.LLM(**cfg)

    # --- Pricing (all values returned are **per 1,000,000 tokens**) ---

    @abstractmethod
    def get_input_cost(self) -> float:
        """Price per 1M input tokens."""
        ...

    @abstractmethod
    def get_cached_input_cost(self) -> float:
        """Price per 1M cached input tokens."""
        ...

    @abstractmethod
    def get_output_cost(self) -> float:
        """Price per 1M output tokens."""
        ...

    def get_options(self) -> str:
        return (
            f"Model: {self.model_name}, Temperature: {self.temperature}, "
            f"Max Tokens: {self.max_tokens}, Presence Penalty: {self.presence_penalty}, "
            f"Additional Options: {self.kwargs}"
        )

    def get_cost(self):
        """Convenience bundle of costs (all per 1M tokens)."""
        return {
            "input": self.get_input_cost(),
            "cached_input": self.get_cached_input_cost(),
            "output": self.get_output_cost(),
        }


# ----------------------------
# Concrete configs + pricing
# ----------------------------

class GPT4_1Config(BaseLLMConfig):
    """
    OpenAI gpt-4.1
    Input: $2.00 / 1M
    Cached input: $0.50 / 1M
    Output: $8.00 / 1M
    """
    def __init__(
        self,
        model_name: str = "gpt-4.1",
        temperature: float = 0.7,
        max_tokens: int = 5000,
        presence_penalty: float = 0.5,
        **kwargs: Any
    ):
        super().__init__(model_name, temperature, max_tokens, presence_penalty, **kwargs)

    def get_input_cost(self) -> float:
        return 2.00 / 1_000_000

    def get_cached_input_cost(self) -> float:
        return 0.50 / 1_000_000

    def get_output_cost(self) -> float:
        return 8.00 / 1_000_000


class GPT4oConfig(BaseLLMConfig):
    """
    OpenAI gpt-4o
    Input: $2.50 / 1M
    Cached input: $1.25 / 1M
    Output: $10.00 / 1M
    """
    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 5000,
        presence_penalty: float = 0.5,
        **kwargs: Any
    ):
        super().__init__(model_name, temperature, max_tokens, presence_penalty, **kwargs)

    def get_input_cost(self) -> float:
        return 2.50 / 1_000_000

    def get_cached_input_cost(self) -> float:
        return 1.25 / 1_000_000

    def get_output_cost(self) -> float:
        return 10.00 / 1_000_000


class GPT4oZeroTempConfig(GPT4oConfig):
    """
    Same pricing as gpt-4o.
    """
    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.0,
        max_tokens: int = 5000,
        presence_penalty: float = 0.5,
        **kwargs: Any
    ):
        super().__init__(model_name=model_name, temperature=temperature,
                         max_tokens=max_tokens, presence_penalty=presence_penalty, **kwargs)


class GPT5Config(BaseLLMConfig):
    """
    OpenAI gpt-5
    Input: $1.25 / 1M
    Cached input: $0.125 / 1M
    Output: $10.00 / 1M
    """
    def __init__(
        self,
        model_name: str = "gpt-5",
        temperature: float = 0.7,
        max_tokens: int = 6000,
        presence_penalty: float = 0.6,
        **kwargs: Any
    ):
        super().__init__(model_name, temperature, max_tokens, presence_penalty, **kwargs)

    def get_input_cost(self) -> float:
        return 1.25 / 1_000_000

    def get_cached_input_cost(self) -> float:
        return 0.125 / 1_000_000

    def get_output_cost(self) -> float:
        return 10.00 / 1_000_000


class GPT5ZeroTempConfig(GPT5Config):
    """
    Same pricing as gpt-5.
    """
    def __init__(
        self,
        model_name: str = "gpt-5",
        temperature: float = 0.0,
        max_tokens: int = 6000,
        presence_penalty: float = 0.6,
        **kwargs: Any
    ):
        super().__init__(model_name=model_name, temperature=temperature,
                         max_tokens=max_tokens, presence_penalty=presence_penalty, **kwargs)


class GPT5MiniConfig(BaseLLMConfig):
    """
    OpenAI gpt-5-mini
    Input: $0.25 / 1M
    Cached input: $0.025 / 1M
    Output: $2.00 / 1M
    """
    def __init__(
        self,
        model_name: str = "gpt-5-mini",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        presence_penalty: float = 0.5,
        **kwargs: Any
    ):
        super().__init__(model_name, temperature, max_tokens, presence_penalty, **kwargs)

    def get_input_cost(self) -> float:
        return 0.25 / 1_000_000

    def get_cached_input_cost(self) -> float:
        return 0.025 / 1_000_000

    def get_output_cost(self) -> float:
        return 2.00 / 1_000_000


class GPT5NanoConfig(BaseLLMConfig):
    """
    OpenAI gpt-5-nano
    Input: $0.05 / 1M
    Cached input: $0.005 / 1M
    Output: $0.40 / 1M
    """
    def __init__(
        self,
        model_name: str = "gpt-5-nano",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        presence_penalty: float = 0.4,
        **kwargs: Any
    ):
        super().__init__(model_name, temperature, max_tokens, presence_penalty, **kwargs)

    def get_input_cost(self) -> float:
        return 0.05 / 1_000_000

    def get_cached_input_cost(self) -> float:
        return 0.005 / 1_000_000

    def get_output_cost(self) -> float:
        return 0.40 / 1_000_000


# Ready-to-use LLM instances
gpt_41_llm = GPT4_1Config().create_llm()
gpt_41_llm_blog_post = GPT4_1Config().create_llm()

gpt_4o_llm = GPT4oConfig().create_llm()
gpt_4o_llm_blog_post = GPT4oConfig().create_llm()
gpt_4o_zero_temp_llm = GPT4oZeroTempConfig().create_llm()

gpt_5_llm = GPT5Config().create_llm()
gpt_5_zero_temp_llm = GPT5ZeroTempConfig().create_llm()

gpt_5_mini_llm = GPT5MiniConfig().create_llm()
gpt_5_mini_llm_blog_post = GPT5MiniConfig(max_tokens=15000).create_llm()
gpt_5_nano_llm = GPT5NanoConfig().create_llm()
