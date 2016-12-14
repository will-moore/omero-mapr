import json
from collections import OrderedDict


def config_list_to_dict(config_list):
    config_dict = OrderedDict()
    for i in json.loads(config_list):
        k = i.get('menu', None)
        if k is not None:
            if i.get('config', None) is not None:
                config_dict[k] = i['config']
    return config_dict
