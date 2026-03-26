from llama_cpp import Llama
from llama_cpp.llama_types import CreateChatCompletionResponse
from datetime import date
from typing import cast
import sys

MODEL_PATH = 'models/Qwen3-4B-Q4_K_M.gguf'
today_f = date.today().strftime('%d/%m/%Y')

def contains_required_char(substring: str) -> bool:
    """
    Return True if the substring contains at least one English letter,
    Cyrillic letter, or digit; otherwise return False.

    English letters: A-Z, a-z
    Digits: 0-9
    Cyrillic letters: characters from the main Cyrillic Unicode blocks
    (Basic Cyrillic, Cyrillic Supplement, Cyrillic Extended-A/B/C).
    """
    def is_cyrillic(ch: str) -> bool:
        code = ord(ch)
        # Unicode blocks covering Cyrillic letters
        return (
            (0x0400 <= code <= 0x04FF) or  # Basic Cyrillic
            (0x0500 <= code <= 0x052F) or  # Cyrillic Supplement
            (0x2DE0 <= code <= 0x2DFF) or  # Cyrillic Extended-A
            (0xA640 <= code <= 0xA69F) or  # Cyrillic Extended-B
            (0x1C80 <= code <= 0x1C8F)     # Cyrillic Extended-C
        )

    for ch in substring:
        if 'A' <= ch <= 'Z' or 'a' <= ch <= 'z':
            return True
        if '0' <= ch <= '9':
            return True
        if is_cyrillic(ch):
            return True
    return False

class LLMEngine:
    def __init__(self, model_path: str):
        self.llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=3000,
            n_threads=8,
            n_gpu_layers=-1, 
            n_batch=512,
            verbose=False)

    def extract(self, prompt: str, system_prompt_path: str):

        if not contains_required_char(prompt):
            return prompt

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

    def construct_replacement_prompt(self, system_prompt_path: str, vals: dict) -> None:
        
        with open(system_prompt_path, 'r') as fin:
            system_prompt = fin.read()

        for k,v in vals:
            system_prompt = system_prompt.replace("{{"+k+"}}", v)

        self.replacement_prompt = system_prompt

    def replace_in_chunk(self, chunk_text: str):

        if not contains_required_char(chunk_text):
            return chunk_text

        resp = cast(
            CreateChatCompletionResponse,
            self.llm.create_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": self.replacement_prompt
                    },
                    {
                        "role": "user",
                        "content": chunk_text+"\n\n/no think"
                    }
                ],
                max_tokens=1024,
                temperature=0.1,
                streaming=False,
            )
        )

        resp_content = resp["choices"][0]["message"]["content"]

        if resp_content is None:
            return chunk_text
        
        resp_clipped = resp_content[resp_content.find('</think>')+len('</think>'):].strip()

        return resp_clipped