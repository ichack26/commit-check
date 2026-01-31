# src/test.py

class Outer:
    def outer_method(self, x):
        return x * 2

    class Inner:
        def inner_method(self, y):
            return y + 10

        def call_outer(self, val):
            # Accessing Outer method from inner
            o = Outer()
            return o.outer_method(val)

    class DeepInner:
        class Nested:
            def nested_method(self, z):
                return z ** 2

def free_function(a):
    return a + 100

# Using classes and functions
def main():
    o = Outer()
    inner = Outer.Inner()
    deep = Outer.DeepInner.Nested()

    res1 = o.outer_method(5)
    res2 = inner.inner_method(7)
    res3 = inner.call_outer(3)
    res4 = deep.nested_method(4)
    res5 = free_function(10)

    # Direct class method call without instance
    res6 = Outer.Inner().inner_method(8)

    print(res1, res2, res3, res4, res5, res6)


if __name__ == "__main__":
    main()
