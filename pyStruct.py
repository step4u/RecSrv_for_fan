from collections import namedtuple

RecordStartRequest = namedtuple("RecordStartRequest", "cmd id device remote_number remote_name local_number local_name dir codec")
RecordStartResponse = namedtuple("RecordStartResponse", "cmd id result reason server port")

