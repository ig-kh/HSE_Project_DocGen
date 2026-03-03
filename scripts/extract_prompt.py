from llama_cpp import Llama
from datetime import date
import time
import numpy as np
from tqdm import tqdm
 
today_f = date.today().strftime('%d/%m/%Y')

MODEL_PATH = 'models/Qwen3-8B-Q4_K_M.gguf'

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=4096,
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
    messages = [
        {
            "role": "system",
            "content": sys_prompt
        },
        {
            "role": "user",
            "content": f"Текущая дата (today) = {today_f}. Если в запросе встречаются слова «сегодня/завтра/вчера», интерпретируй их относительно этой даты. Если срок работ задан длительностью (например, «2 недели», «10 дней», «1 месяц»), считай начало работ = date договора и вычисляй конец периода."
        },
        {
            "role": "user",
            "content": "Привет, составь мне договор с МТС от сегодняшнего дня по поводу продажи 1000 коров на сумму 1 миллион рублей, срок исполнения 2 недели с момента заключения договора"
        }
    ]
)
print(f"Prompt processing time: {np.mean(time.time() - start)}")

print(resp["choices"][0]["message"]["content"])