import django
if django.VERSION < (1, 8):
    raise RuntimeError('MAPR requires Django 1.8+')

from django.conf import settings


class MaprSettings(object):

    MAPR_MENU_CUSTOM = {
        'gene': {
            'default': ('Gene Symbol', ),
            'all': ('Gene Symbol', 'Gene Identifier', ),
            'label': ('Gene', ),
            'ns': (
                'openmicroscopy.org/mapr/gene',
            ),
        },
        'phenotype': {
            'default': ('Phenotype', ),
            'all': ('Phenotype', 'Phenotype Term Accession', ),
            'label': ('Phenotype', ),
            'ns': (
                'openmicroscopy.org/mapr/phenotype',
            ),
        },
        'compound': {
            'default': ('Compound Name', ),
            'all': ('Compound Name', ),
            'label': ('Compound', ),
            'ns': (
                'openmicroscopy.org/omero/compund',
            ),
        },
        'sirna': {
            'default': ('siRNA Identifier', ),
            'all': ('siRNA Identifier', ),
            'label': ('siRNA', ),
            'ns': (
                'openmicroscopy.org/mapr/sirna',
            ),
        },
    }

    MENU_MAPR = getattr(settings, 'MAPR_MENU_CUSTOM', MAPR_MENU_CUSTOM)

mapr_settings = MaprSettings()
