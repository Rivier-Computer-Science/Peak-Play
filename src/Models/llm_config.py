# Example usage:
# gpt_41_llm = GPT4_1Config().create_llm()
# print(GPT4_1Config().get_options())
# print(GPT4_1Config().get_cost())

import langchain_openai as lang_oai
from abc import ABC, abstractmethod

class BaseLLMConfig(ABC):
    def __init__(self, model_name, temperature, max_tokens, presence_penalty, **kwargs):
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.presence_penalty = presence_penalty
        self.kwargs = kwargs

    def create_llm(self):
        return lang_oai.ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            presence_penalty=self.presence_penalty,
            **self.kwargs
        )

    @abstractmethod
    def get_input_cost(self):
        pass

    @abstractmethod
    def get_output_cost(self):
        pass

    def get_options(self):
        return f"Model: {self.model_name}, Temperature: {self.temperature}, Max Tokens: {self.max_tokens}, Presence Penalty: {self.presence_penalty}, Additional Options: {self.kwargs}"

    def get_cost(self):
        return {
            "input": self.get_input_cost(),
            "output": self.get_output_cost()
        }


class GPT4_1Config(BaseLLMConfig):
    def __init__(self):
        super().__init__(model_name="gpt-4.1", temperature=0.7, max_tokens=5000, presence_penalty=0.5)

    def get_input_cost(self):
        return 2.00 / 1000  # cost per 1k tokens (input)

    def get_output_cost(self):
        return 8.00 / 1000  # cost per 1k tokens (output)


class GPT4oConfig(BaseLLMConfig):
    def __init__(self):
        super().__init__(model_name="gpt-4o", temperature=0.7, max_tokens=5000, presence_penalty=0.5)

    def get_input_cost(self):
        return 2.50 / 1000  # cost per 1k tokens (input)

    def get_output_cost(self):
        return 10.00 / 1000  # cost per 1k tokens (output)


class GPT4oZeroTempConfig(BaseLLMConfig):
    def __init__(self):
        super().__init__(model_name="gpt-4o", temperature=0.0, max_tokens=5000, presence_penalty=0.5)

    def get_input_cost(self):
        return 2.50 / 1000  # cost per 1k tokens (input)

    def get_output_cost(self):
        return 10.00 / 1000  # cost per 1k tokens (output)


class GPT5Config(BaseLLMConfig):
    def __init__(self):
        super().__init__(model_name="gpt-5", temperature=0.7, max_tokens=6000, presence_penalty=0.6)

    def get_input_cost(self):
        return 1.25 / 1000  # cost per 1k tokens (input)

    def get_output_cost(self):
        return 10.00 / 1000  # cost per 1k tokens (output)


class GPT5ZeroTempConfig(BaseLLMConfig):
    def __init__(self):
        super().__init__(model_name="gpt-5", temperature=0.0, max_tokens=6000, presence_penalty=0.6)

    def get_input_cost(self):
        return 1.25 / 1000  # cost per 1k tokens (input)

    def get_output_cost(self):
        return 10.00 / 1000  # cost per 1k tokens (output)


class GPT5MiniConfig(BaseLLMConfig):
    def __init__(self):
        super().__init__(model_name="gpt-5-mini", temperature=0.7, max_tokens=4000, presence_penalty=0.5)

    def get_input_cost(self):
        return 0.25 / 1000  # cost per 1k tokens (input)

    def get_output_cost(self):
        return 2.00 / 1000  # cost per 1k tokens (output)


class GPT5NanoConfig(BaseLLMConfig):
    def __init__(self):
        super().__init__(model_name="gpt-5-nano", temperature=0.7, max_tokens=2000, presence_penalty=0.4)

    def get_input_cost(self):
        return 0.05 / 1000  # cost per 1k tokens (input)

    def get_output_cost(self):
        return 0.40 / 1000  # cost per 1k tokens (output)


# Instantiations of all derived classes
gpt_41_llm = GPT4_1Config().create_llm()
gpt_41_llm_blog_post = GPT4_1Config().create_llm()
gpt_4o_llm = GPT4oConfig().create_llm()
gpt_4o_llm_blog_post = GPT4oConfig().create_llm()
gpt_4o_zero_temp_llm = GPT4oZeroTempConfig().create_llm()
gpt_5_llm = GPT5Config().create_llm()
gpt_5_zero_temp_llm = GPT5ZeroTempConfig().create_llm()
gpt_5_mini_llm = GPT5MiniConfig().create_llm()
gpt_5_nano_llm = GPT5NanoConfig().create_llm()



