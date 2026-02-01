import test

def fun2(x):    
    def f():
        return 4
    a = fun1(x)
    b = f()
    return a + b