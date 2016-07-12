from django.conf import settings


class MaprSettings(object):

    MAPR_MENU_CUSTOM = {
        'gene': {
            'default': ('Gene Symbol', ),
            'all': ('Gene Symbol', 'Gene Identifier', ),
            'label': ('Gene', ),
        },
        'phenotype': {
            'default': ('Phenotype', ),
            'all': ('Phenotype', ),
            'label': ('Phenotype', ),
        },
        'compound': {
            'default': ('Compound Name', ),
            'all': ('Compound Name', ),
            'label': ('Compound', ),
        },
        'sirna': {
            'default': ('siRNA Identifier', ),
            'all': ('siRNA Identifier', ),
            'label': ('siRNA', ),
        },
    }

    MENU_MAPR = getattr(settings, 'MAPR_MENU_CUSTOM', MAPR_MENU_CUSTOM)

    MAPR_MENU_DEFAULT = {
        'default': {
            'default': ('Gene Symbol', ),
            'all': ('Gene Symbol', 'Gene Identifier', 'Phenotype',
                    'Compound Name', 'siRNA Identifier', ),
        }
    }

    DEFAULT_MAPR = getattr(settings, 'MAPR_MENU_DEFAULT', MAPR_MENU_DEFAULT)

mapr_settings = MaprSettings()
