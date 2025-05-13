from typing import List
from llama_index.llms.replicate import Replicate
from llama_index.llms.llama_cpp.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)

LLAMA_13B_V2_CHAT = "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5"


class CustomLlama2(Replicate):
    def __init__(self, model=LLAMA_13B_V2_CHAT, temperature=0.01, context_window=4096, completion_to_prompt=None, messages_to_prompt=None):
        super().__init__(model=model, temperature=temperature, context_window=context_window, completion_to_prompt=completion_to_prompt, messages_to_prompt=messages_to_prompt)
        self.model = model
        self.temperature = temperature
        self.context_window = context_window
        self.completion_to_prompt = completion_to_prompt
        self.messages_to_prompt = messages_to_prompt

    def custom_completion_to_prompt(self, completion: str) -> str:
        return completion_to_prompt(
            completion,
            system_prompt=(
                "You are a Q&A assistant. Your goal is to answer questions as "
                "accurately as possible is the instructions and context provided."
            ),
        )

    def custom_messages_to_prompt(self, messages: List[str]) -> str:
        return messages_to_prompt(messages)

    def replicate(self, messages: List[str], max_tokens: int = 100) -> str:
        return super().replicate(messages, max_tokens)

    def __call__(self, messages: List[str], max_tokens: int = 100) -> str:
        return self.replicate(messages, max_tokens)

# The replicate endpoint


# inject custom system prompt into llama-2
# def custom_completion_to_prompt(completion: str) -> str:
#     return completion_to_prompt(
#         completion,
#         system_prompt=(
#             "You are a Q&A assistant. Your goal is to answer questions as "
#             "accurately as possible is the instructions and context provided."
#         ),
#     )


# llm = Replicate(
#     model=LLAMA_13B_V2_CHAT,
#     temperature=0.01,
#     # override max tokens since it's interpreted
#     # as context window instead of max tokens
#     context_window=4096,
#     # override completion representation for llama 2
#     completion_to_prompt=custom_completion_to_prompt,
#     # if using llama 2 for data agents, also override the message representation
#     messages_to_prompt=messages_to_prompt,
# )
