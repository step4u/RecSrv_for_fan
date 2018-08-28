import threading as th
import socket
import sys, getopt
from pyStructs import RecordCmd

class RecordServer(object):
    print_lock = th.Lock()

    def __init__(self, host=socket.gethostname(), port=10000, listen=10):
        self.s = socket.socket()
        self.host = host
        self.port = port
        self.listen = listen

    def start(self, arg='tcp'):
        if (arg == 'tcp'):
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        print("host:port / listen = " + str(self.host) + ":" + str(self.port) + " / " + str(self.listen))

        if (arg == 'tcp'):
            self.s.bind((self.host, self.port))
            self.s.listen(self.listen)
        else:
            self.s.bind((self.host, self.port))
        
        while True:
            if (arg == 'tcp'):
                con, addr = self.s.accept()
                print('Got connection from', addr)
                RecordServer.print_lock.acquire()
                th._start_new_thread(self.tcpThreaded, (con,))
            else:
                RecordServer.print_lock.acquire()
                th._start_new_thread(self.udpThreaded, (self.s,))

    def tcpThreaded(self, con):
        while True:
            strrcv = con.recv(1024).decode()
            print("received: " + strrcv)

            recCmd = RecordCmd()
            recCmd.parse(strrcv)

            if (recCmd.command["cmd"] == "RecordStartRequest"):
                recCmd.command = {
                    "cmd": "RecordStartResponse",
                    "id": recCmd.command["id"],
                    "result": "success",
                    "reason": "",
                    "server": self.host,
                    "port": 10020
                }

                con.send(recCmd.serialize().encode())
                print("sent: " + recCmd.serialize())
                
                recudp = RecordServer()
                recudp.start('udp')

            elif (recCmd.command["cmd"] == "RecordStopRequest"):
                print("RecordStopRequested")
                RecordServer.print_lock.release()
                break

        con.close()

    def udpThreaded(self, s):
        while True:
            data = s.recvfrom(1024)
            print("received: " + data)

def main(argv):
    host, port, listen = getOption(argv)
    recServer = RecordServer(host, port, listen)
    recServer.start()

def getOption(argv):
    host = "192.168.0.8"
    port = 10000
    listen = 5

    try:
        opts, args = getopt.getopt(argv,"?h:p:l:",["host=","port=", "listen="])
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
    # print("Host:port: " + host + ":" + str(port) + "/ listen: " + str(listen))
    return host, port, listen

if __name__ == '__main__':
    main(sys.argv[1:])
