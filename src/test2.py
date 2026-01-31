import test

def fun2(x):    
    def f():
        return 4

    return fun1(x) + f()