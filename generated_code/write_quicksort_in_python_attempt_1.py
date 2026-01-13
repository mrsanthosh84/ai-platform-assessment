def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

if __name__ == "__main__":
    arr = [64, 34, 25, 12, 22, 11, 90]
    sorted_arr = quicksort(arr)
    print(f"Sorted array: {sorted_arr}")

import unittest

class TestQuicksort(unittest.TestCase):
    def test_quicksort(self):
        self.assertEqual(quicksort([3, 1, 4, 1, 5]), [1, 1, 3, 4, 5])
        self.assertEqual(quicksort([]), [])
        self.assertEqual(quicksort([1]), [1])