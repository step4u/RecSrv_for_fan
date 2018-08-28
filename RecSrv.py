import threading, socket, struct
import os, sys, getopt, platform, datetime
import wave, audioop
from pyStructs import RecordCmd

ports = [[x, 0] for x in range(12000,13000,1)]
threads = []
threadsinfo = []
exitFlag = False

class RecThread(threading.Thread):
    def __init__(self, thinfo):
        threading.Thread.__init__(self)
        self.info = thinfo
    def run(self):
        recThreaded(self.info)
    def setExitFlag(self, flag):
        self.info[1] = flag

def getAvailbleUdpPort(udpport):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        try:
            s.bind((host, udpport))
            s.close()
            break
        except:
            udpport = udpport + 1
    return udpport

def udpPortsInit(x):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind((socket.gethostname(), x[0]))
    except:
        x[1] = 1
    s.close()
    return x

def getAvailblePort():
    availablePorts = list(map(udpPortsInit, ports))
    return min(list(filter(lambda x: x[1]==0, availablePorts)))[0]

def getOption(argv):
    host = "192.168.0.8"
    port = 10000
    listen = 10
    filepath = os.getenv("HOME")
    if (platform.system() == "Windows"):
        filepath = os.getenv("APPDATA") + "\\Fanvil\\recorded"
    else:
        filepath = os.getenv("HOME") + "/.fanvil/recorded"

    try:
        opts, args = getopt.getopt(argv,"?h:p:l:f:",["host=","port=", "listen=", "filepath="])
    except getopt.GetoptError:
        print('-h <host> -p <port> -l <number>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-?", "--help"):
            print('-h <host> -p <port> -l <number>')
            sys.exit()
        elif opt in ("-h", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-l", "--listen"):
            listen = int(arg)
        elif opt in ("-f", "--filepath"):
            filepath = arg
    return host, port, listen, filepath

def cmdThreaded(con, filepath):
    udpport = 41000

    while True:
        strrcv = con.recv(1024).decode()
        print("received: " + strrcv)

        recCmd = RecordCmd(strrcv)
        recvedcmd = recCmd.command

        udpport = getAvailbleUdpPort(udpport)

        if (recCmd.command["cmd"] == "RecordStartRequest"):
            recCmd.command = {
                "cmd": "RecordStartResponse",
                "id": recvedcmd["id"],
                "result": "success",
                "reason": "",
                "server": host,
                "port": udpport
            }

            # print('received command0: ' + str(recvedcmd))
            # print('received command1: ' + str(recCmd.command))

            recsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            recsock.bind((host, udpport))
            threadinfo = [recvedcmd, False, recsock, filepath]

            recthread = RecThread(threadinfo)
            recthread.start()
            threads.append(recthread)
            
            con.send(recCmd.serialize().encode())
            print("sent: " + recCmd.serialize())
        elif (recCmd.command["cmd"] == "RecordStopRequest"):
            print("RecordStopRequested")
            recthread = list(filter(lambda x: x.info[0]["id"]==recvedcmd["id"], threads))
            print('RecordStopRequested: thread info1: ' + str(recthread[0].info))
            s = recthread[0].info[2]
            # recthread[0].setExitFlag(True)
            if (udpport > s.getsockname()[1]):
                udpport = s.getsockname()[1]
            s.close()
            print('RecordStopRequested: thread info2: ' + str(recthread[0].info))
            threads.remove(recthread[0])
            print('RecordStopRequested: threads: ' + str(threads))
            print('RecordStopRequested: udpport: ' + str(udpport))
            break

    con.close()
    print("Command Thread Terminated...")

def recThreaded(info):
    cmd = info[0]
    sock = info[2]
    filepath = info[3]
    filename = ''
    datetimenow = datetime.datetime.now()

    if (cmd["dir"] == 'out'):
        filename = (cmd["dir"]
            + '_' + cmd["local_number"]
            + '_' + cmd["remote_number"]
            + '_' + cmd["device"]
            + '_' + datetimenow.strftime('%Y-%m-%d_%H_%M_%S')
            + '.wav')
    else:
        filename = (cmd["dir"]
            + '_' + cmd["remote_number"]
            + '_' + cmd["local_number"]
            + '_' + cmd["device"]
            + '_' + datetimenow.strftime('%Y-%m-%d_%H_%M_%S')
            + '.wav')

    if (platform.system() == 'Windows'):
        filepath = filepath + '\\' + datetimenow.strftime('%Y-%m-%d')
        if (not os.path.exists(filepath)):
            os.makedirs(filepath)
        filepath = filepath + '\\' + filename
    else:
        filepath = filepath + '/' + datetimenow.strftime('%Y-%m-%d')
        if (not os.path.exists(filepath)):
            os.makedirs(filepath)
        filepath = filepath + '/' + filename

    f = open(filepath, 'wb')
    wav = wave.open(filepath, 'wb')
    wav.setparams((1, 2, 8000, 8000*1, 'NONE', 'not compressed'))

    while not info[1]:
        try:
            data = sock.recv(1024)
            # print(str(len(data)))
            if (cmd["codec"] == 'PCMU'):
                wav.writeframes(audioop.ulaw2lin(data[12:], 2))
            elif (cmd["codec"] == 'PCMA'):
                wav.writeframes(audioop.alaw2lin(data[12:], 2))
            elif (cmd["codec"] == 'G722'):
                continue
            else:
                wav.writeframes(audioop.ulaw2lin(data[12:], 2))
        except OSError as e:
            if (e.errno == 10038):
                if (f is not None): f.close()
                if (wav is not None): wav.close()
                print("UDP terminated: {0} / {1}".format(e.errno, e.strerror))
                print("UDP terminated normally.")
                break
            else:
                print("recThreaded errno: {0} / {1}".format(e.errno, e.strerror))
                continue

    if (f is not None): f.close()
    if (wav is not None): wav.close()
    if (sock is not None): sock.close()
    print("Recorder Thread Terminated..." + str(info[0]))


### Program Start
host, port, listen, filepath = getOption(sys.argv[1:])
print('Initialized Options: {0}/{1}/{2}/{3}'.format(host, port, listen, filepath))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen(listen)

while not exitFlag:
    try:
        con, addr = s.accept()
        print('Got connection from', addr)
        threading.Thread(target=cmdThreaded, args=(con,filepath,)).start()
    except:
        exitFlag = True
        print("RecSrv terminated as a unexpected reason.")

for thread in threads:
    thread.join()

print("Terminated main thread.")

# def main(argv):
#     exitFlag = False
#     host, port, listen = getOption(argv)
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind((host, port))
#     s.listen(listen)

#     while not exitFlag:
#         try:
#             con, addr = s.accept()
#             print('Got connection from', addr)
#             th.Thread(target=cmdThreaded, args=(con,))
#         except:
#             exitFlag = True
#             print("Terminated as a unexpected reason.")

#     for thread in threads:
#         thread.join()

# if __name__ == '__main__':
#     main(sys.argv[1:])
