from agent import FreyaAgentNL

def main():
    """Lance la boucle interactive avec FREYA."""
    try:
        freya = FreyaAgentNL()
        print("Bienvenue dans FREYA (NL), ton assistant personnel.")
        print("Tape 'exit' pour quitter.\n")
        
        while True:
            try:
                message = input("Vous: ").strip()
                if not message:
                    continue
                if message.lower() in ["exit", "quit"]:
                    print("FREYA: À bientôt !")
                    break
                response = freya.respond(message)
                print(f"FREYA: {response}\n")
            except KeyboardInterrupt:
                print("\nFREYA: Interruption détectée. À bientôt !")
                break
    except Exception as e:
        print(f"Erreur critique: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
