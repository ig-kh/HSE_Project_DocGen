from llama_cpp import Llama
from llama_cpp.llama_types import CreateChatCompletionResponse
from datetime import date
from typing import cast
import sys

MODEL_PATH = 'models/Qwen3-8B-Q4_K_M.gguf'
today_f = date.today().strftime('%d/%m/%Y')


class LLMExtractor:
    def __init__(self, model_path: str):
        self.llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=3000,
            n_threads=6,
            n_batch=512,
            verbose=False)

    def extract(self, prompt: str, system_prompt_path: str):
        with open(system_prompt_path, 'r') as fin:
            system_prompt = fin.read()

        resp = cast(
            CreateChatCompletionResponse,
            self.llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"today={today_f}. 'сегодня/завтра/вчера' считать относительно today."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1024,
                stream=False
            )
        )
        
        content = resp["choices"][0]["message"]["content"]

        if content is None:
            content = ""
        
        if '</think>' in content:
            content = content.split('</think>')[-1].strip()

        return content
