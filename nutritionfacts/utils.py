import json
import zlib

def load_zipped_json(data):
    try:
        data = zlib.decompress(data)
    except:
        pass
    return json.loads(data.decode('utf-8'))