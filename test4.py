import time, threading

def method1(param):
    param = param + 1
    print("method1: param: " + str(param))

def method2(param):
    param = param + 1
    print("method2: param: " + str(param))

def method3(param):
    param[0] = param[0] + 1
    param[1] = param[1] + 1
    while param[2]:
        print("method3: param: " + str(param))
        time.sleep(3)

    print("method3 was ended: " +  str(param))

a = 1
b = 2
method1(a)
method2(b)
c = [a, b, True]
# method3(c)

print(str(a))
print(str(b))
print(str(c))

c[0] = c[0] + 1
c[1] = c[1] + 1

t = threading.Thread(target=method3, args=(c,))
t.start()
time.sleep(9)
c[2] = False

t.join()

print("end")
