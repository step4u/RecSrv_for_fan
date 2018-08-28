class RTP(object):
    def __init__(self, bytes):
        self.packet = bytes
        self.Ver = None
        self.Padding = None
        self.eXtension = None
        self.CSRC = None
        self.Marker = None
        self.PayloadType = None
        self.Sequence = None
        self.Timestamp = None
        self.SSRCID = None
    def parse(self):
        
