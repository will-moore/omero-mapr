import django
from django.conf import settings
from omeroweb.settings import process_custom_settings, report_settings
import sys
import json


if django.VERSION < (1, 8):
    raise RuntimeError('MAPR requires Django 1.8+')

# load settings
MAPR_SETTINGS_MAPPING = {
    "omeroweb.mapr.config":
        ["MAPR_CONFIG", '[]',
         json.loads,
         None],
    }

process_custom_settings(sys.modules[__name__], 'MAPR_SETTINGS_MAPPING')
report_settings(sys.modules[__name__])


class MaprSettings(object):

    MENU_MAPR = getattr(settings, 'MAPR_CONFIG', MAPR_CONFIG)  # noqa

mapr_settings = MaprSettings()
