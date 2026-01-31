class foo:
    def bars(x):
        return 2 * x

def b(x):
    return foo.bars(x + 1)

def ab(x):
    return 3 + b(x)

def new(x):
    print(1)
    return 3 * x

def h(x):
    return x + new(x)

z = ab(1)
print(z)
y = 3 + z * 3
print(y)
print(y * z)