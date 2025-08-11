# Example usage:
# gpt_41_llm = GPT4_1Config().create_llm()
# print(GPT4_1Config().get_options())
# print(GPT4_1Config().get_cost())

from abc import ABC, abstractmethod
from typing import Any, Dict
import pprint
import crewai as crewai
import src.Utils.utils as utils


class BaseLLMConfig(ABC):
    def __init__(
        self,
        model_name: str = "gpt-4o",
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

        self.logger = utils.configure_logger()
        

    def _needs_max_completion_tokens(self, model_id: str) -> bool:
        """
        OpenAI Responses-API families that require `max_completion_tokens`
        instead of `max_tokens`. Covers gpt-5* and o*-series models.
        """
        name = model_id.split("/")[-1].lower()
        return name.startswith(("gpt-5", "o1", "o3", "o4"))

    def create_llm(self, **overrides: Any) -> crewai.LLM:
        """
        Return a crewai.LLM instance ready to use in agents.
        Automatically uses `max_completion_tokens` for models that require it.
        """
        # Resolve core fields (overrides win)
        model = overrides.pop("model", overrides.pop("model_name", self.model_name))
        provider = overrides.pop("provider", self.kwargs.get("provider", "openai"))
        temperature = overrides.pop("temperature", self.temperature)
        presence_penalty = overrides.pop("presence_penalty", self.presence_penalty)
        num_retries = overrides.pop("num_retries", self.kwargs.get("num_retries", self.num_retries))
        timeout = overrides.pop("timeout", self.kwargs.get("timeout", self.timeout))

        # Token limits: accept both names; map to what's required by the model family
        max_tokens_default = self.max_tokens
        max_tokens = overrides.pop("max_tokens", max_tokens_default)
        max_completion_tokens = overrides.pop("max_completion_tokens", None)

        # Merge extra kwargs (api_key, base_url, top_p, etc.)
        final_kwargs = {**self.kwargs, **overrides}

        # Normalize / drop keys we set explicitly
        for k in (
            "model_name", "provider",
            "max_tokens", "max_completion_tokens",
            "temperature", "presence_penalty", "num_retries", "timeout"
        ):
            final_kwargs.pop(k, None)

        # Build a provider-qualified model id (recommended by CrewAI/LiteLLM)
        model_id = model if "/" in model else f"{provider}/{model}"

        # Decide which token field to send
        if max_completion_tokens is not None:
            tokens_field = {"max_completion_tokens": max_completion_tokens}
        else:
            if self._needs_max_completion_tokens(model_id):
                tokens_field = {"max_completion_tokens": max_tokens}
            else:
                tokens_field = {"max_tokens": max_tokens}

        cfg: Dict[str, Any] = {
            "model": model_id,
            "temperature": temperature,
            "presence_penalty": presence_penalty,
            "num_retries": num_retries,
            "timeout": timeout,
            # tolerate unknown params across providers
            "drop_params": True,
            "additional_drop_params": ["model_name"],
            **tokens_field,
            **final_kwargs,
        }

        self.logger.debug("Creating LLM")
        self.logger.info(pprint.pprint(cfg, sort_dicts=False, width=80))
        return crewai.LLM(**cfg)

    # --- Pricing (all values returned are **per token**) ---

    @abstractmethod
    def get_input_cost(self) -> float:
        """Price per input token."""
        ...

    @abstractmethod
    def get_cached_input_cost(self) -> float:
        """Price per cached input token."""
        ...

    @abstractmethod
    def get_output_cost(self) -> float:
        """Price per output token."""
        ...

    def get_options(self) -> str:
        return (
            f"Model: {self.model_name}, Temperature: {self.temperature}, "
            f"Max Tokens: {self.max_tokens}, Presence Penalty: {self.presence_penalty}, "
            f"Additional Options: {self.kwargs}"
        )

    def get_cost(self):
        """Convenience bundle of costs (all per token)."""
        return {
            "input": self.get_input_cost(),
            "cached_input": self.get_cached_input_cost(),
            "output": self.get_output_cost(),
        }


# ----------------------------
# Concrete configs + pricing
# (all prices per token)
# ----------------------------

class GPT4_1Config(BaseLLMConfig):
    """
    OpenAI gpt-4.1
    Input: $2.00 / 1M  ->  2.0e-6 per token
    Cached input: $0.50 / 1M -> 5.0e-7 per token
    Output: $8.00 / 1M -> 8.0e-6 per token
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
        return 2.0e-6

    def get_cached_input_cost(self) -> float:
        return 5.0e-7

    def get_output_cost(self) -> float:
        return 8.0e-6


class GPT4oConfig(BaseLLMConfig):
    """
    OpenAI gpt-4o
    Input: $2.50 / 1M  ->  2.5e-6 per token
    Cached input: $1.25 / 1M -> 1.25e-6 per token
    Output: $10.00 / 1M -> 1.0e-5 per token
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
        return 2.5e-6

    def get_cached_input_cost(self) -> float:
        return 1.25e-6

    def get_output_cost(self) -> float:
        return 1.0e-5


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
        super().__init__(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            **kwargs
        )


class GPT5Config(BaseLLMConfig):
    """
    OpenAI gpt-5
    Input: $1.25 / 1M  ->  1.25e-6 per token
    Cached input: $0.125 / 1M -> 1.25e-7 per token
    Output: $10.00 / 1M -> 1.0e-5 per token
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
        self.logger.info("GPT5Config LLM Initialized")

    def get_input_cost(self) -> float:
        return 1.25e-6

    def get_cached_input_cost(self) -> float:
        return 1.25e-7

    def get_output_cost(self) -> float:
        return 1.0e-5


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
        super().__init__(
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            **kwargs
        )
        self.logger.info("GPT5ZeroTempConfig LLM Initialized")


class GPT5MiniConfig(BaseLLMConfig):
    """
    OpenAI gpt-5-mini
    Input: $0.25 / 1M  ->  2.5e-7 per token
    Cached input: $0.025 / 1M -> 2.5e-8 per token
    Output: $2.00 / 1M -> 2.0e-6 per token
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
        self.logger.info("GPT5MiniConfig LLM Initialized")

    def get_input_cost(self) -> float:
        return 2.5e-7

    def get_cached_input_cost(self) -> float:
        return 2.5e-8

    def get_output_cost(self) -> float:
        return 2.0e-6


class GPT5NanoConfig(BaseLLMConfig):
    """
    OpenAI gpt-5-nano
    Input: $0.05 / 1M  ->  5.0e-8 per token
    Cached input: $0.005 / 1M -> 5.0e-9 per token
    Output: $0.40 / 1M -> 4.0e-7 per token
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
        self.logger.info("GPT5NanoConfig LLM Initialized")

    def get_input_cost(self) -> float:
        return 5.0e-8

    def get_cached_input_cost(self) -> float:
        return 5.0e-9

    def get_output_cost(self) -> float:
        return 4.0e-7


# Ready-to-use LLM instances (crewai.LLM objects)
# gpt_41_llm = GPT4_1Config().create_llm()
# gpt_41_llm_blog_post = GPT4_1Config().create_llm()

# gpt_4o_llm = GPT4oConfig().create_llm()
# gpt_4o_llm_blog_post = GPT4oConfig().create_llm()
# gpt_4o_zero_temp_llm = GPT4oZeroTempConfig().create_llm()

# gpt_5_llm = GPT5Config().create_llm()
# gpt_5_zero_temp_llm = GPT5ZeroTempConfig().create_llm()

# gpt_5_mini_llm = GPT5MiniConfig().create_llm()
# gpt_5_mini_llm_blog_post = GPT5MiniConfig(max_tokens=15000).create_llm()
# gpt_5_nano_llm = GPT5NanoConfig().create_llm()
