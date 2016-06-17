from django.conf import settings


class MapSettings(object):

    CUSTOM_MENU_MAPPER = {
        'gene': {
            'default': ('Gene Symbol', ),
            'all': ('Gene Symbol', 'Gene Identifier', ),
        },
        'phenotype': {
            'default': ('Phenotype', ),
            'all': ('Phenotype', ),
        },
        'compound': {
            'default': ('Compound Name', ),
            'all': ('Compound Name', ),
        },
        'sirna': {
            'default': ('siRNA Identifier', ),
            'all': ('siRNA Identifier', ),
        },
    }

    MENU_MAPPER = getattr(settings, 'MAP_MENU_MAPPER', CUSTOM_MENU_MAPPER)

    DEFAULT_MENU_MAPPER = {
        'default': {
            'default': ('Gene Symbol', ),
            'all': ('Gene Symbol', 'Gene Identifier', 'Phenotype',
                    'Compound Name', 'siRNA Identifier', ),
        }
    }

    DEFAULT_MAPPER = getattr(settings, 'MAP_MENU_MAPPER', DEFAULT_MENU_MAPPER)

map_settings = MapSettings()
