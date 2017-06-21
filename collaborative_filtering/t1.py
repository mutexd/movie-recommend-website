
def fib(n):
    a, b = 0, 1
    while b < n:
        print b,
        a, b = b, a+b

print "I'm global script, being imported"

if __name__ == "__main__":
    import sys
    print "I'm executed as main"
