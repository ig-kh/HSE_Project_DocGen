from llama_cpp import Llama


class LLMExtractor:

    def __init__(self, model_path: str):

        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_threads=8
        )

    def extract(self, prompt: str):

        system_prompt = """
Extract structured contract fields from user input.
Return JSON only.
"""

        full_prompt = f"""
{system_prompt}

User input:
{prompt}
"""

        output = self.llm(full_prompt)

        return output["choices"][0]["text"]