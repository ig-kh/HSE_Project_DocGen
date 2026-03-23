from llama_cpp import Llama, LlamaGrammar
from datetime import date
import time
import json
import numpy as np
from tqdm import tqdm
from pydantic import ValidationError
from json_validator import validate_llm_json
 
today_f = date.today().strftime('%d/%m/%Y')

MODEL_PATH = 'models/Qwen3-8B-Q4_K_M.gguf'

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=3000,
    n_threads=6,
    n_batch=512,
    verbose=False
)

with open('scripts/system_prompt.txt', 'r') as fin:
    sys_prompt = fin.read()
    
# print(len(sys_prompt))
# exit(0)
start = time.time()
resp = llm.create_chat_completion(
    messages=[
        {
            "role": "system",
            "content": sys_prompt
        },
        {
            "role": "user",
             "content": f"today={today_f}. 'сегодня/завтра/вчера' считать относительно today."
        },
        {
            "role": "user",
            "content": "Привет, составь мне договор с ООО 'Бабки деньги бизнес' от 25 апреля 2026 года по поводу скама 10 бабушек на общую сумму в 100 тысяч рублей, срок исполнения 2 дня"
        }
    ],
    max_tokens=1024
)
print(f"Prompt processing time: {np.mean(time.time() - start)}")

resp_content = resp["choices"][0]["message"]["content"]
if '</think>' in resp_content:
    print('Removing thinking block...')
    resp_content = resp_content[resp_content.find('</think>')+len('</think>'):].strip()
print(resp_content)

try:
    parsed = validate_llm_json(resp_content)
    print("OK:", parsed.model_dump())
except json.JSONDecodeError as e:
    print("Not JSON:", e)
except ValidationError as e:
    print("Schema error:\n", e)