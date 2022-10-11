def A():
    x = [100, 200]
    B(x)
    print(x)


def B(x):
    x[1] = x[1] + 1


A()