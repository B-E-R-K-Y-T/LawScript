
def test(x_):
    if x_ > 10:
        return False
    else:
        return True

x = 1

while test(x):
    print(x)
    x += 1
