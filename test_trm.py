"""Test du modèle DeepSeek R1 1.5B avec llama-cpp-python"""

from llama_cpp import Llama
import time

# Chemin du modèle
MODEL_PATH = "DeepSeek-R1-Distill-Qwen-1.5B-Q8_0.gguf"

print("🚀 Chargement du modèle DeepSeek R1 1.5B...")
print("⏳ Cela peut prendre quelques secondes...\n")

start_load = time.time()

# Charger le modèle
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,        # Contexte
    n_threads=4,       # Threads CPU
    n_gpu_layers=0,   # Layers sur GPU (ajustez selon votre VRAM)
    verbose=False
)

load_time = time.time() - start_load
print(f"✅ Modèle chargé en {load_time:.2f}s\n")

# Questions de test
test_prompts = [
    "Create script Python for calcultaing factorial of a number.",

]

for i, prompt in enumerate(test_prompts, 1):
    print(f"{'='*50}")
    print(f"🔹 Test {i}: {prompt}")
    print(f"{'='*50}")
    
    start_gen = time.time()
    
    response = llm(
        prompt,
        max_tokens=256,
        temperature=0.7,
        stop=["</s>", "\n\n\n"]
    )
    
    gen_time = time.time() - start_gen
    output = response["choices"][0]["text"].strip()
    
    print(f"📝 Réponse:\n{output}")
    print(f"\n⏱️ Temps de génération: {gen_time:.2f}s")
    print(f"📊 Tokens générés: {response['usage']['completion_tokens']}")
    print()

print("✅ Tests terminés!")
