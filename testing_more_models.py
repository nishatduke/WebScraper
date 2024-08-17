from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline,AutoModel,AutoModelForQuestionAnswering
import os
from dotenv import load_dotenv
import torch

load_dotenv()


tokene = os.getenv("LLAMA_CHAT")
local_model_path = "C:\\Users\\nisha\\llama2_test\\Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(local_model_path)
model = AutoModelForCausalLM.from_pretrained(local_model_path)
extra_model = AutoModelForQuestionAnswering.from_pretrained(local_model_path)


device = 0 if torch.cuda.is_available() else -1

messages = [
    {"role": "user", "content": "What is the sentimient of the following text(as a score between 1-10)?: The company profit is up super high and I am super happy!"},
]
pipe = pipeline("text-generation", model="meta-llama/Llama-2-7b-chat-hf")


response = pipe(messages)
print(response)
print("THe sentiment score is 10")
