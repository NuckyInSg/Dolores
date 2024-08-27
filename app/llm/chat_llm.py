import tiktoken
from typing import Any, List, Optional

ONE_MILLION = 1_000_000

class ChatLLM:
    def __init__(self, model: Any,
                 cost_million_input_token: float,
                 cost_million_output_token: float,
                 max_output_token: int,
                 context_window: int,
                 encoder="cl100k_base",
                 **kwargs):
        self.model = model
        self.cost_million_input_token = cost_million_input_token
        self.cost_million_output_token = cost_million_output_token
        self.max_output_token = max_output_token
        self.tokenizer = tiktoken.get_encoding(encoder)
        self.context_window = context_window

        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0

    def num_tokens_from_string(self, string: str) -> int:
        return len(self.tokenizer.encode(string))

    def update_token_usage(self, input_tokens: str, output_tokens: str):
        self.total_input_tokens += len(self.tokenizer.encode(input_tokens))
        self.total_output_tokens += len(self.tokenizer.encode(output_tokens))
        
    def compute_cost(self) -> float:
        input_cost = self.cost_million_input_token * self.total_input_tokens / ONE_MILLION
        output_cost = self.cost_million_output_token * self.total_output_tokens / ONE_MILLION
        return input_cost + output_cost
    
    def get_token_usage(self):
        total_tokens = self.total_input_tokens + self.total_output_tokens
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": total_tokens,
            "total_cost": f"${self.compute_cost():.4f}",
            "context_percentage": (total_tokens / self.context_window) * 100
        }
    
    def __getattr__(self, name: str) -> Any:
        return getattr(self.model, name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.model.invoke(*args, **kwargs)