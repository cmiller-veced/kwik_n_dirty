"""
A decorator is a function that takes a function as its sole argument and
returns a function.
"""

# It can be the same function.
def flagged(fun):
    fun.flag = True
    return fun


@flagged
def f1():
    return

def f2():
    return

"""
>>> f1
<function f1 at 0x10415b1f0>
>>> f2
<function f2 at 0x10415b310>
>>> f1.flag
True
>>> f2.flag
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'function' object has no attribute 'flag'
"""


# ##########################################

# More interesting decorators.


def double(fun):
    def inner(arg):
        return 2 * fun(arg)
    return inner

@double
def i2(arg):
    return arg

# The @ syntax is exactly equivalent to 
def i4(arg):
    return arg
i4 = double(i4)


assert i2('abc ') == i4('abc ') == 'abc abc '
assert i2(2) == i4(2) == 4


# ##########################################
# Scoping

# Variables of the enclosing function are visible to the inner function.

def logged(fun):
    print(f'{fun} defined')
    def inner(arg):
        print(f'{fun} run with {arg}')  # Note that `fun` is visible here.
        return fun(arg)
    return inner


@logged
def f3(arg):
    return arg
"""
>>> f3('x')
<function f3 at 0x10415b0d0> run with x
'x'
>>> f3(2)
<function f3 at 0x10415b0d0> run with 2
2
"""


# ##########################################
# Memoize


def recall(fun):
    cache = {}
    def inner(n):
        if n not in cache:
            cache[n] = fun(n)
        return cache[n]
    return inner


@recall
def fact(n):
    if n == 0:
        return 1
    return n * fact(n-1)

@recall
def fib(n):
    if n == 0 or n == 1:
        return 1
    return fib(n-1) + fib(n-2)

"""
Without the memoization, these functions run into recursion limits.
Oops.  That is not true anymore.
"""

def fact2(n):
    if n == 0:
        return 1
    return n * fact2(n-1)

"""
The memoize decorator is a good one to practice for understanding scoping but
the standard lib contains the same.
"""
from functools import lru_cache


@lru_cache
def fact3(n):
    if n == 0:
        return 1
    return n * fact3(n-1)



# ##########################################
# Closures

"""
A closure is a function defined inside a function, together with the variables
of the enclosing function.
"""

def enclosing():
    thing = 0
    def inner():
        nonlocal thing
        thing += 1
        print(f'the value is {thing}')
    return inner

c1 = enclosing()    # c1 is a closure
c2 = enclosing()    # another closure
"""
>>> c1()
the value is 1
>>> c1()
the value is 2
>>> c2()
the value is 1
>>> c1()
the value is 3

Most of the decorators above are closures.

One good way to think of it is....

An object is data with associated function(s).
A closure is a function with associated data.

"""


# ##########################################
# Parameterized decorator

def multiply_by(n):
    def outer(fun):
        def inner(arg):
            return n * fun(arg)
        return inner
    return outer

@multiply_by(3)
def i3(arg):
    return arg

assert i3('x') == 'xxx'
assert i3(2) == 6


def ident(arg):
    return arg

by4 = multiply_by(4)(ident)
by5 = multiply_by(5)(ident)
assert by4('x') == 'xxxx'
assert by4(2) == 8
assert by5('x') == 'xxxxx'
assert by5(2) == 10


# ##########################################


