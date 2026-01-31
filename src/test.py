class foo:
    def bars(x):
        return 2 * x

def b(x):
    return foo.bars(x)

def a(x):
    return 3 + b(x)

z = a(1)
print(z)
y = 3 + z * 3
print(y)
print(y * z)