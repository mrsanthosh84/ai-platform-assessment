def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]

def fibonacci_iterative(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

if __name__ == "__main__":
    n = 10
    print(f"Fibonacci({n}) with memoization: {fibonacci_memo(n)}")
    print(f"Fibonacci({n}) iterative: {fibonacci_iterative(n)}")

import unittest

class TestFibonacci(unittest.TestCase):
    def test_fibonacci_memo(self):
        self.assertEqual(fibonacci_memo(0), 0)
        self.assertEqual(fibonacci_memo(1), 1)
        self.assertEqual(fibonacci_memo(10), 55)
    
    def test_fibonacci_iterative(self):
        self.assertEqual(fibonacci_iterative(0), 0)
        self.assertEqual(fibonacci_iterative(1), 1)
        self.assertEqual(fibonacci_iterative(10), 55)