import threading

class RecThread(threading.Thread):
    def __init__(self, thinfo):
        self.info = thinfo
    def run(self):
        pass
