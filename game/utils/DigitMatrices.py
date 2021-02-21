import numpy as np

def vectorize(arr):
    return np.array([[int(el) for el in list(row)] for row in arr]).T

zero = [
    "111",
    "101",
    "101",
    "101",
    "111",
]
one = [
    "010",
    "010",
    "010",
    "010",
    "010",
]
two = [
    "111",
    "001",
    "111",
    "100",
    "111"
]
three = [
    "111",
    "001",
    "111",
    "001",
    "111"
]
four = [
    "101",
    "101",
    "111",
    "001",
    "001"
]
five = [
    "111",
    "100",
    "111",
    "001",
    "111"
]
six = [
    "111",
    "100",
    "111",
    "101",
    "111"
]
seven = [
    "111",
    "001",
    "001",
    "001",
    "001"
]
eight = [
    "111",
    "101",
    "111",
    "101",
    "111"
]
nine = [
    "111",
    "101",
    "111",
    "001",
    "111"
]

digits = [
    vectorize(zero),
    vectorize(one),
    vectorize(two),
    vectorize(three),
    vectorize(four),
    vectorize(five),
    vectorize(six),
    vectorize(seven),
    vectorize(eight),
    vectorize(nine)
]
DIGIT_MATRIX_SIZE = digits[0].shape
