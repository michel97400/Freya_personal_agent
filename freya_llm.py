# freya_llm.py
from groq import Groq
from dotenv import load_dotenv
load_dotenv() 
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_groq(prompt, history=None):
    messages = []
    if history:
        messages.extend(history)
    messages.append({"role":"user", "content": prompt})
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages
    )
    return response.choices[0].message.content
