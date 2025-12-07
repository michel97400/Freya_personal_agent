import sys

def factorial(n):
    if n < 0:
        raise ValueError("La factorielle n'est pas définie pour les nombres négatifs")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test.py <nombre>")
        sys.exit(1)
    try:
        number = int(sys.argv[1])
        print(f"Factorielle de {number} = {factorial(number)}")
    except ValueError as e:
        print(f"Erreur: {e}")
