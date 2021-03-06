import threading, socket, struct
import os, sys, getopt, platform, datetime
import wave, audioop
import mysql.connector
from mysql.connector import errorcode
import subprocess as sb
from pyStructs import RecordCmd

# ports = [[x, 0] for x in range(12000,13000,1)]
threads = []
# threadsinfo = []
exitFlag = False

class RecThread(threading.Thread):
    def __init__(self, thinfo):
        threading.Thread.__init__(self)
        self.info = thinfo
    def run(self):
        recThreaded(self.info)
    def setExitFlag(self, flag):
        self.info[1] = flag
    def force2terminate(self):
        try:
            if self.isAlive():
                self.info[1] = True
                self.info[2].shutdown(socket.SHUT_RD)
                self.info[2].close()
                # raise threading.ThreadError("The tread will be terminated.")
        except:
            pass

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

'''
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
'''

def getOption(argv):
    # host = socket.gethostname()
    host = '192.168.0.8'
    port = 10000
    listen = 10
    filepath = os.getenv("HOME")
    dbhost = '192.168.0.18'
    if (platform.system() == "Windows"):
        filepath = os.getenv("APPDATA") + "\\Fanvil\\recorded"
    else:
        filepath = os.getenv("HOME") + "/fanvil/recorded"

    try:
        opts, args = getopt.getopt(argv,"?h:p:l:f:db:",["host=","port=", "listen=", "filepath=", "dbhost="])
    except getopt.GetoptError:
        print('Usage : -h <host> -p <port> -l <number> -f <savepath> -db <dbhost>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-?", "--help"):
            print('Usage : -h <host> -p <port> -l <number> -f <savepath> -db <dbhost>')
            print('Default save path is "{0}"'.format(filepath))
            sys.exit()
        elif opt in ("-h", "--host"):
            host = arg
        elif opt in ("-p", "--port"):
            port = int(arg)
        elif opt in ("-l", "--listen"):
            listen = int(arg)
        elif opt in ("-f", "--filepath"):
            filepath = arg
        elif opt in ("-db", "--dbhost"):
            dbhost = arg
    return host, port, listen, filepath, dbhost

def cmdThreaded(con, filepath, dbhost):
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

            recsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # recsock.settimeout(60)
            recsock.bind((host, udpport))
            threadinfo = [recvedcmd, False, recsock, filepath]

            recthread = RecThread(threadinfo)
            recthread.start()
            threads.append(recthread)
            
            con.send(recCmd.serialize().encode())
            print("sent RecordStartResponse: " + recCmd.serialize())
        elif (recCmd.command["cmd"] == "RecordStopRequest"):
            print("RecordStopRequested")

            recCmdRes = RecordCmd()
            recCmdRes.command = {
                "cmd": "RecordStopResponse",
                "id": recvedcmd["id"],
                "result": "success",
            }

            recthread = list(filter(lambda x: x.info[0]["id"]==recvedcmd["id"], threads))
            if (udpport > recthread[0].info[2].getsockname()[1]):
                udpport = recthread[0].info[2].getsockname()[1]
            oldcmd = recthread[0].info[0]

            savepath = recthread[0].info[3].replace("\\", "/")
            savefilename = recthread[0].info[4]

            recthread[0].force2terminate()
            recthread[0].join()
            threads.remove(recthread[0])
            # print('RecordStopRequested: udpport: ' + str(udpport))

            dbconfig = {
                'host':dbhost,
                'user':'fanvilkr',
                'password':'fanvilkrAs!',
                'database':'fanvilrecord'
            }

            cnx = cur = None
            try:
                cnx = mysql.connector.connect(**dbconfig)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print('Something is wrong with your user name or password.')
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print('Database does not exist')
                else:
                    print(err)
            else:
                try:
                    sql = "insert into record (direction, mac, remote_number, remote_name, local_number, local_name, savepath, filename) values ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}')".format(oldcmd["dir"], oldcmd["device"], oldcmd["remote_number"], oldcmd["remote_name"], oldcmd["local_number"], oldcmd["local_name"], savepath, savefilename)
                    cur = cnx.cursor()
                    cur.execute(sql)
                    cnx.commit()
                except mysql.connector.Error as err:
                    cnx.rollback()
                    print("Database err: " + err.msg)
            finally:
                if cur:
                    cur.close()
                if cnx:
                    cnx.close()
                
            ### Send RecordStopResponse
            con.send(recCmdRes.serialize().encode())
            print("sent RecordStopResponse: " + recCmdRes.serialize())
            break

    con.close()
    print("Command Thread Terminated...")

def recThreaded(info):
    cmd = info[0]
    filepath = info[3]
    filename = ''
    info.append(filename)
    writer = None
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

    info[4] = filename

    if (platform.system() == 'Windows'):
        filepath = filepath + '\\' + datetimenow.strftime('%Y-%m-%d')
        if (not os.path.exists(filepath)):
            os.makedirs(filepath)
        info[3] = filepath
        filepath = filepath + '\\' + filename
    else:
        filepath = filepath + '/' + datetimenow.strftime('%Y-%m-%d')
        if (not os.path.exists(filepath)):
            os.makedirs(filepath)
        info[3] = filepath
        filepath = filepath + '/' + filename
    info.append(filepath)

    codec = cmd["codec"].lower()

    if (codec == 'pcmu' or codec == 'pcma'):
        writer = wave.open(filepath, 'wb')
        writer.setparams((1, 2, 8000, 8000*1, 'NONE', 'not compressed'))
    else:
        ecodec = 'pcm_s16le'
        if (sys.byteorder == 'big'):
            ecodec = 'pcm_s16be'
        # ar = None
        if (codec == 'g723'):
            codec = codec + '_1'
        elif ('g726' in codec):
            if (sys.byteorder == 'little'):
                codec = 'g726le'
            else:
                codec = 'g726'

        #-nostats -loglevel 0
        # , '-nostats'
        # , '-loglevel', '0'
        command = ['ffmpeg'
        , '-f', codec
        , '-ac', '1'
        , '-i', '-'
        , '-ar', '8k'
        , '-ac', '1'
        , '-acodec'
        , ecodec
        , filepath]
        writer = sb.Popen(command, stdin=sb.PIPE)

    while not info[1]:
        '''
        data = info[2].recv(1024)
        # print(str(len(data)))
        if (cmd["codec"] == 'PCMU'):
            # f.write(data[12:])
            writer.writeframes(audioop.ulaw2lin(data[12:], 2))
        elif (cmd["codec"] == 'PCMA'):
            # f.write(data[12:])
            writer.writeframes(audioop.alaw2lin(data[12:], 2))
        elif (cmd["codec"] == 'G722'):
            writer.stdin.write(data[12:])
        else:
            writer.stdin.write(data[12:])
        '''
        try:
            data = info[2].recv(1024)
            if (len(data) < 1):
                break
            if (codec == 'pcmu'):
                writer.writeframes(audioop.ulaw2lin(data[12:], 2))
            elif (codec == 'pcma'):
                writer.writeframes(audioop.alaw2lin(data[12:], 2))
            else:
                # G722, G723, G726-32
                writer.stdin.write(data[12:])
        except OSError as e:
            print('UDP socket status: ' + e.strerror)
            if (e.errno == 10038):
                print('Check writer status: ' + str(writer is None))
                try:
                    writer.stdin.close()
                    writer.wait()
                except:
                    if (writer is not None):
                        writer.close()
                print("UDP terminated: {0} / {1}".format(e.errno, e.strerror))
                print("UDP terminated normally.")
                break
            else:
                print("recThreaded errno: {0} / {1}".format(e.errno, e.strerror))
                continue

    try:
        writer.stdin.close()
        writer.wait()
    except:
        if (writer is not None):
            writer.close()
    if (info[2] is not None):
        info[2].close()
    print("Recorder Thread Terminated..." + str(info[0]))


### Program Start
host, port, listen, filepath, dbhost = getOption(sys.argv[1:])
# print('Initialized Options: {0}/{1}/{2}/{3}/{4}'.format(host, port, listen, filepath, dbhost))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind((host, port))
    s.listen(listen)
except OSError as e:
    if (e.errno == 99):
        print('Local Network Error: {0}'.format(e.strerror))
        sys.exit()

while not exitFlag:
    con, addr = s.accept()
    print('Got connection from', addr)
    threading.Thread(target=cmdThreaded, args=(con,filepath,dbhost)).start()

    '''
    try:
        con, addr = s.accept()
        print('Got connection from', addr)
        threading.Thread(target=cmdThreaded, args=(con,filepath,)).start()
    except:
        exitFlag = True
        print("RecSrv terminated as a unexpected reason.")
    '''

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
