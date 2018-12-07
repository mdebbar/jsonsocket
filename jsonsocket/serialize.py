import json

use_numpy, use_pandas = True, True
try:
    import numpy as np
except ImportError:
    use_numpy = False

try:
    import pandas as pd
except ImportError:
    use_pandas = False


class BetterEncoder(json.JSONEncoder):
    def default(self, obj):
        if use_numpy and isinstance(obj, np.ndarray):
            return obj.tolist()

        if use_pandas and (isinstance(obj, pd.DataFrame) or isinstance(obj, pd.Series)):
            res = dict(_decode_type=obj.__class__.__name__, _content=obj.to_dict())
            return res
        return json.JSONEncoder.default(self, obj)


class BetterDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(BetterDecoder, self).__init__(object_hook=self.default, *args, **kwargs)

    def default(self, obj):
        if use_pandas and isinstance(obj, dict):
            if "_decode_type" in obj and "_content" in obj:
                obj = eval("pd.%s(obj[\"_content\"])" % obj["_decode_type"])
        return obj


def serialize(data):
    try:
        res = json.dumps(data, cls=BetterEncoder).encode('utf-8')
    except (TypeError, ValueError) as e:
        raise Exception('You can only send JSON-serializable data')
    return res


def deserialize(data):
    try:
        res = json.loads(data.decode('utf-8'), cls=BetterDecoder)
    except (TypeError, ValueError) as e:
        raise Exception('Data received was not in JSON format')
    return res
