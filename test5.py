import time, threading, socket

def method1(param):
    param[0]
    try:
        while param[0]:
            data = param[1].recv(1024)
            print("method3: param: " + str(data))
            time.sleep(1)
    except:
        pass    
    print("method1 was ended")

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('192.168.0.23', 10003))
# s.settimeout(10)
c = [True, s]

t = threading.Thread(target=method1, args=(c,))
t.start()
time.sleep(5)
c[0] = False
c[1].shutdown(socket.SHUT_RD)
# c[0].close()
print(str(c[1]))
print("Tried...")

t.join()

print("end")
