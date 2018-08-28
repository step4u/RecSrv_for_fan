# from pyStructs import RecordStartRequest, RecordStartResponse

# from urllib.parse import urlparse, parse_qs, parse_qsl

# parsed_url = urlparse("cmd=RecordStartResponse&id=15082&result=success&reason=&server=192.168.0.8&port=10020")
# print(parsed_url)
# parsed_qs = parse_qs(parsed_url.path)
# print(parsed_qs)
# parsed_qsl = parse_qsl(parsed_url.path)
# parsed_dict = dict(parsed_qsl)
# print(type(parsed_dict))
# print(parsed_dict)
# print(parsed_dict["cmd"])
# parsed_dict["cmd"] = 'tttt'
# print(parsed_dict["cmd"])

# req = RecordStartRequest()
# req.request["cmd"] = "ddd"
# req.request["id"] = "123123"
# req.request["device"] = "asdfasdf"
# req.request["remote_number"] = "90001"
# req.request["remote_name"] = "90001"
# req.request["local_number"] = "90001"
# req.request["local_name"] = "90001"
# req.request["dir"] = "out"
# req.request["codec"] = "ulaw"
# reqQs = req.serialize()
# print(reqQs)

# portrange = range(10000, 10100, 1)
# for p in portrange:
#     print(p)
