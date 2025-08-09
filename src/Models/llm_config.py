# Example usage:
# gpt_41_llm = GPT4_1Config().create_llm()
# print(GPT4_1Config().get_options())
# print(GPT4_1Config().get_cost())

import langchain_openai as lang_oai
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseLLMConfig(ABC):
    def __init__(
        self,
        model_name: str,
        temperature: float,
        max_tokens: int,
        presence_penalty: float,
        **kwargs: Any
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.presence_penalty = presence_penalty
        # Extra args (api_key, base_url, timeout, etc.)
        self.kwargs: Dict[str, Any] = dict(kwargs)

    def create_llm(self, **overrides: Any):
        """
        Build a ChatOpenAI with either the stored defaults or per-call overrides.
        Example: create_llm(max_tokens=2048, temperature=0.0)
        """
        model_name = overrides.pop("model_name", self.model_name)
        temperature = overrides.pop("temperature", self.temperature)
        max_tokens = overrides.pop("max_tokens", self.max_tokens)
        presence_penalty = overrides.pop("presence_penalty", self.presence_penalty)
        final_kwargs = {**self.kwargs, **overrides}

        return lang_oai.ChatOpenAI(
            model_name=model_name,              # keep 'model_name' for compatibility with your env
            temperature=temperature,
            max_tokens=max_tokens,
            presence_penalty=presence_penalty,
            **final_kwargs
        )

    @abstractmethod
    def get_input_cost(self) -> float:
        pass

    @abstractmethod
    def get_output_cost(self) -> float:
        pass

    def get_options(self) -> str:
        return (
            f"Model: {self.model_name}, Temperature: {self.temperature}, "
            f"Max Tokens: {self.max_tokens}, Presence Penalty: {self.presence_penalty}, "
            f"Additional Options: {self.kwargs}"
        )

    def get_cost(self):
        return {
            "input": self.get_input_cost(),
            "output": self.get_output_cost()
        }


class GPT4_1Config(BaseLLMConfig):
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
        return 2.00 / 1000  # cost per 1k tokens (input)

    def get_output_cost(self) -> float:
        return 8.00 / 1000  # cost per 1k tokens (output)


class GPT4oConfig(BaseLLMConfig):
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
        return 2.50 / 1000

    def get_output_cost(self) -> float:
        return 10.00 / 1000


class GPT4oZeroTempConfig(BaseLLMConfig):
    def __init__(
        self,
        model_name: str = "gpt-4o",
        temperature: float = 0.0,
        max_tokens: int = 5000,
        presence_penalty: float = 0.5,
        **kwargs: Any
    ):
        super().__init__(model_name, temperature, max_tokens, presence_penalty, **kwargs)

    def get_input_cost(self) -> float:
        return 2.50 / 1000

    def get_output_cost(self) -> float:
        return 10.00 / 1000


class GPT5Config(BaseLLMConfig):
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
        return 1.25 / 1000

    def get_output_cost(self) -> float:
        return 10.00 / 1000


class GPT5ZeroTempConfig(BaseLLMConfig):
    def __init__(
        self,
        model_name: str = "gpt-5",
        temperature: float = 0.0,
        max_tokens: int = 6000,
        presence_penalty: float = 0.6,
        **kwargs: Any
    ):
        super().__init__(model_name, temperature, max_tokens, presence_penalty, **kwargs)

    def get_input_cost(self) -> float:
        return 1.25 / 1000

    def get_output_cost(self) -> float:
        return 10.00 / 1000


class GPT5MiniConfig(BaseLLMConfig):
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
        return 0.25 / 1000

    def get_output_cost(self) -> float:
        return 2.00 / 1000


class GPT5NanoConfig(BaseLLMConfig):
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
        return 0.05 / 1000

    def get_output_cost(self) -> float:
        return 0.40 / 1000


# Instantiations of all derived classes
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
