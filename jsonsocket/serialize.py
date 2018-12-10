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

        if use_pandas:
            typename = obj.__class__.__name__
            res=None
            if isinstance(obj, pd.DataFrame):
                content = dict(zip(obj.columns, obj.values.T.tolist()))
                for key, value in content.items():
                    unique = np.unique(value)
                    if len(unique)==1:
                        content[key] = unique[0]
                res = dict(_decode_type=typename, _content=content)
            elif isinstance(obj, pd.Series):
                res = dict(_decode_type=typename, _content=obj.to_dict())
            if res:
                return res
        if "int" == type(obj).__name__[:3]:
            return int(obj)
        if "float" == type(obj).__name__[:5]:
            return float(obj)
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
        raise Exception('You can only send JSON-serializable data. Error is : %s' % e)
    return res


def deserialize(data):
    if type(data) == bytes:
        data = data.decode('utf-8')
    try:
        res = json.loads(data, cls=BetterDecoder)
    except (TypeError, ValueError) as e:
        raise Exception('Data received was not in JSON format')
    return res
