import test

def fun2(x):
    def f():
        return 3

    return fun1(x) + f()