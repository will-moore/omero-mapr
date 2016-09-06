from django.conf import settings


class MaprSettings(object):

    MAPR_MENU_CUSTOM = {
        'gene': {
            'default': ('Gene Symbol', ),
            'all': ('Gene Symbol', 'Gene Identifier', ),
            'label': ('Gene', ),
            'ns': (
                'openmicroscopy.org/mapr/gene',
                'openmicroscopy.org/omero/bulk_annotations'
            ),
        },
        'phenotype': {
            'default': ('Phenotype', ),
            'all': ('Phenotype', 'Phenotype Term Accession', ),
            'label': ('Phenotype', ),
            'ns': (
                'openmicroscopy.org/mapr/phenotype',
                'openmicroscopy.org/omero/bulk_annotations'
            ),
        },
        'compound': {
            'default': ('Compound Name', ),
            'all': ('Compound Name', ),
            'label': ('Compound', ),
            'ns': (
                'openmicroscopy.org/omero/compund',
                'openmicroscopy.org/omero/bulk_annotations'
            ),
        },
        'sirna': {
            'default': ('siRNA Identifier', ),
            'all': ('siRNA Identifier', ),
            'label': ('siRNA', ),
            'ns': (
                'openmicroscopy.org/mapr/sirna',
                'openmicroscopy.org/omero/bulk_annotations'
            ),
        },
    }

    MENU_MAPR = getattr(settings, 'MAPR_MENU_CUSTOM', MAPR_MENU_CUSTOM)

mapr_settings = MaprSettings()
