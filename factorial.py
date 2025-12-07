class Factoriel:
    def __init__(self, n):
        self.n = n

    def compute(self):
        """Calculate factorial of n using recursion."""
        if self.n == 0:
            return 1
        else:
            return self.n * Factoriel(self.n - 1).compute()
