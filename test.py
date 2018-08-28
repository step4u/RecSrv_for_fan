import os, subprocess, platform, time, socket

ports = [[x, 0] for x in range(100,1000,1)]
# print(len(lists))
# for p in lists:
#     print(p)

def listFilter(x):
    strcmd = "netstat -an | grep -i udp | awk 'match($2, /:" + str(x[0]) + "$/) { sum+=1 }; END { print sum }'"
    val = subprocess.check_output(strcmd, shell=True)
    try:
        count = int(val.rstrip())
    except:
        count = 0

    print(str(x[0]) + ": " + str(count))

    if count > 0:
        x[1] = 1

    return x

def portsInit(x):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind((socket.gethostname(), x[0]))
    except:
        x[1] = 1

    s.close()

    return x

now = time.time()
result = list(map(portsInit, ports))
now2 = time.time()
print(now2 - now)
#print(result)
result2 = filter(lambda x: x[1]==0, result)
filtered0 = list(result2)
print(filtered0)
filtered1 = min(filtered0)
print(filtered1)
# print(len(filtered))
# print(result)

#result[1] = 1

#result = filter(lamda x,y : x==10000, lists)

# import os, subprocess, platform
# #print(os.system('netstat -an | grep -i udp | grep -w 138 | awk "{ sum += $1}; END { print sum}"'))
# #print(os.system('netstat -an | grep -i udp | grep -w 138'))
# #print(os.system("netstat -an | grep -i udp | grep -w 138 | awk '{ sum += 1 }; END { print sum }'"))
# print(platform.system())
# val = subprocess.check_output("netstat -an | grep -i udp | awk 'match($2, /:138$/) { sum+=1 }; END { print sum }'", shell=True)
# try:
#     count = int(val.rstrip())
# except:
#     count = 0
# print(count)
