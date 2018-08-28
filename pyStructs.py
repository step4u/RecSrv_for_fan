from urllib.parse import urlparse, parse_qs, parse_qsl, urlencode

class RecordStartRequest(object):
    def __init__(self):
        self.request = {}

    # def parse(self, qs):
    #     parsed_url = urlparse(qs)
    #     parsed_qsl = parse_qsl(parsed_url.path)
    #     self.request = dict(parsed_qsl)

    def serialize(self):
        return urlencode(self.request)

class RecordStopRequest(object):
    def __init__(self):
        self.request = {}

    # def parse(self, qs):
    #     parsed_url = urlparse(qs)
    #     parsed_qsl = parse_qsl(parsed_url.path)
    #     self.request = dict(parsed_qsl)

    def serialize(self):
        return urlencode(self.request)

class RecordCmd(object):
    def __init__(self, qs):
        self.command = {}
        self.parse(qs)

    def parse(self, qs):
        parsed_url = urlparse(qs)
        parsed_qsl = parse_qsl(parsed_url.path, keep_blank_values=True)
        self.command = dict(parsed_qsl)
        
    def serialize(self):
        return urlencode(self.command)
