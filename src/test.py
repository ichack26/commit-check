# 1️⃣ Change a free function
def free_function(a):
    # old: return a + 100
    return a + 101  # small change

# 2️⃣ Add a print inside a method
class Outer:
    def outer_method(self, x):
        print(f"Outer method called with {x}")  # new line
        return x * 2

# 3️⃣ Slight change in nested class
class Outer:
    class Inner:
        def inner_method(self, y):
            return y + 11  # was 10, small change

# 4️⃣ Add a comment somewhere (optional, should be ignored)
    class DeepInner:
        class Nested:
            def nested_method(self, z):
                # squaring
                return z ** 2
