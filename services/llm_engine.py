from datetime import date
import re
from typing import List, Optional, cast

from llama_cpp import Llama
from llama_cpp.llama_types import CreateChatCompletionResponse

MODEL_PATH = "models/Qwen3-8B-Q4_K_M.gguf"

# ----------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------


def strip_thinking_sections(
    text: str,
    custom_patterns: Optional[List[str]] = None,
    strip_whitespace: bool = True,
) -> str:
    """
    Remove all thinking / reasoning sections from the model's output.

    Supports:
    - XML‑like tags: <thinking>, <thought>, <reasoning>, <cot>, <chain_of_thought>
    - Cyrillic tags: <размышление>
    - Chinese tags: 思考, 推理 (until end of line or paragraph)
    - Markdown blocks: ### Thinking, **Thinking:**
    - Separators: ---, ***

    Args:
        text: Raw output string.
        custom_patterns: Additional regex patterns to remove.
        strip_whitespace: Whether to collapse multiple blank lines and strip.

    Returns:
        Cleaned text with thinking sections removed.
    """
    if not text:
        return text

    base_patterns = [
        # XML‑like tags (case‑insensitive)
        r"<thinking>.*?</thinking>",
        r"<think>.*?</think>",
        r"<thought>.*?</thought>",
        r"<reasoning>.*?</reasoning>",
        r"<cot>.*?</cot>",
        r"<chain_of_thought>.*?</chain_of_thought>",
        r"<размышление>.*?</размышление>",
        # Chinese tags (no closing tag, removed until next blank line or end)
        r"思考[:：]\s*.*?(?=\n\s*\n|\Z)",
        r"推理[:：]\s*.*?(?=\n\s*\n|\Z)",
        # Markdown headings and bold text
        r"###\s*Thinking\s*\n.*?(?=\n###|\n\*\*|\n\Z)",
        r"\*\*Thinking:\*\*\s*.*?(?=\n\s*\n|\Z)",
        # Separators followed by text
        r"---\s*\n.*?(?=\n---|\n\*\*\*|\Z)",
        r"\*\*\*\s*\n.*?(?=\n---|\n\*\*\*|\Z)",
    ]

    patterns = base_patterns.copy()
    if custom_patterns:
        patterns.extend(custom_patterns)

    result = text
    for pattern in patterns:
        result = re.sub(pattern, "", result, flags=re.DOTALL | re.IGNORECASE)

    if strip_whitespace:
        # Collapse multiple blank lines into at most one
        result = re.sub(r"\n\s*\n", "\n\n", result)
        result = result.strip()

    return result


def contains_required_char(substring: str) -> bool:
    """
    Check if the string contains at least one letter (English or Cyrillic) or digit.

    Returns True if any character is:
    - English letter (A-Z, a-z)
    - Digit (0-9)
    - Cyrillic letter (Unicode blocks 0x0400–0x04FF, 0x0500–0x052F,
      0x2DE0–0x2DFF, 0xA640–0xA69F, 0x1C80–0x1C8F)
    """

    def _is_cyrillic(ch: str) -> bool:
        code = ord(ch)
        return (
            (0x0400 <= code <= 0x04FF)  # Basic Cyrillic
            or (0x0500 <= code <= 0x052F)  # Cyrillic Supplement
            or (0x2DE0 <= code <= 0x2DFF)  # Cyrillic Extended‑A
            or (0xA640 <= code <= 0xA69F)  # Cyrillic Extended‑B
            or (0x1C80 <= code <= 0x1C8F)  # Cyrillic Extended‑C
        )

    for ch in substring:
        if "A" <= ch <= "Z" or "a" <= ch <= "z":
            return True
        if "0" <= ch <= "9":
            return True
        if _is_cyrillic(ch):
            return True
    return False


# ----------------------------------------------------------------------
# Main LLM engine class
# ----------------------------------------------------------------------


class LLMEngine:
    """Wrapper around llama_cpp.Llama with thinking‑section removal."""

    def __init__(self, model_path: str) -> None:
        """
        Initialize the LLM engine.

        Args:
            model_path: Path to the GGUF model file.
        """
        self.llm = Llama(
            model_path=MODEL_PATH,  # fixed: use the passed parameter
            n_ctx=3000,
            n_threads=8,
            n_gpu_layers=-1,
            n_batch=512,
            verbose=False,
        )
        self.replacement_prompt = ""  # will be set by construct_replacement_prompt

    def extract(
        self,
        prompt: str,
        system_prompt_path: str,
    ) -> str:
        """
        Process a single prompt using the given system prompt file.

        The system prompt is read from the file. Two user messages are sent:
        one with the current date instruction, and the actual user prompt
        with "/no_think" appended.

        Args:
            prompt: User input text.
            system_prompt_path: Path to the file containing the system prompt.

        Returns:
            Cleaned model response (thinking sections removed).
        """
        # Skip processing if the input contains no letters/digits
        if not contains_required_char(prompt):
            return prompt

        with open(system_prompt_path, "r", encoding="utf-8") as fin:
            system_prompt = fin.read()

        today_str = date.today().strftime("%d/%m/%Y")

        resp = cast(
            CreateChatCompletionResponse,
            self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"today={today_str}. 'сегодня/завтра/вчера' считать относительно today.",
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\n/no_think",
                    },
                ],
                max_tokens=1024,
                stream=False,
            ),
        )

        content = resp["choices"][0]["message"]["content"]
        if content is None:
            return ""

        return strip_thinking_sections(content)

    def construct_replacement_prompt(self, system_prompt_path: str, vals: dict) -> None:
        """
        Load a system prompt template and replace placeholders with values.

        Placeholders in the template should be of the form {{key}}.

        Args:
            system_prompt_path: Path to the template file.
            vals: Dictionary mapping placeholder keys to replacement values.
        """
        with open(system_prompt_path, "r", encoding="utf-8") as fin:
            template = fin.read()

        for key, value in vals.items():
            template = template.replace("{{" + key + "}}", str(value))

        self.replacement_prompt = template

    def replace_in_chunk(self, chunk_text: str) -> str:
        """
        Process a chunk of text using the pre‑loaded replacement prompt.

        The replacement prompt must have been set by calling
        construct_replacement_prompt first.

        Args:
            chunk_text: Input text to be processed.

        Returns:
            Cleaned model response (thinking sections removed).
        """
        if not contains_required_char(chunk_text):
            return chunk_text

        resp = cast(
            CreateChatCompletionResponse,
            self.llm.create_chat_completion(
                messages=[
                    {"role": "system", "content": self.replacement_prompt},
                    {"role": "user", "content": f"{chunk_text}\n\n/no_think"},
                ],
                temperature=0.1,
                stream=False,
            ),
        )

        content = resp["choices"][0]["message"]["content"]
        if content is None:
            return chunk_text

        return strip_thinking_sections(content)
