from freya_llm import ask_groq

history = []
while True:
    user = input("You: ")
    if user.lower() in ["exit","quit"]:
        break
    reply = ask_groq(user, history)
    print("FREYA:", reply)
    history.append({"role":"user", "content": user})
    history.append({"role":"assistant", "content": reply})
