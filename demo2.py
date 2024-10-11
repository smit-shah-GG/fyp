import numpy as np
import os
from sys import path

x = 10
y = x + 5

def foo(a):
    if a > 10:
        return a * 2
    else:
        return a + 1

for i in range(5):
    print(i)