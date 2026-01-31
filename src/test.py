class foo:
    def bar(x):
        return 2 * x

def h(x):
    return foo.bar(x)

def f(x):
    return 3 + h(x)

z = f(1)
print(z)
y = 3 + z * 3
print(y)