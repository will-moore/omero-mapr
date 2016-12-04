import os
import json
import django

from django.conf import settings
from omero_mapr.mapr_settings import config_list_to_dict

# We manually designate which settings we will be using in an environment
# variable. This is similar to what occurs in the `manage.py`
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'omeroweb.settings')


# `pytest` automatically calls this function once when tests are run.
def pytest_configure():
    settings.DEBUG = False
    settings.MAPR_CONFIG = config_list_to_dict(json.dumps(
        [
            {
                "menu": "gene",
                "config": {
                    "default": ["Gene Symbol"],
                    "all": ["Gene Symbol", "Gene Identifier"],
                    "ns": ["openmicroscopy.org/omero/bulk_annotations"],
                    "label": "Gene"
                }
            },
            {
                "menu": "phenotype",
                "config": {
                    "default": ["Phenotype"],
                    "all": ["Phenotype", "Phenotype Term Accession"],
                    "ns": ["openmicroscopy.org/omero/bulk_annotations"],
                    "label": "Phenotype"
                }
            },
            {
                "menu": "organism",
                "config": {
                    "default": ["Organism"],
                    "all": ["Organism"],
                    "ns": ["openmicroscopy.org/omero/bulk_annotations"],
                    "label": "Organism"
                }
            },
            {
                "menu": "others",
                "config": {
                    "default": ["Others"],
                    "all": ["Others"],
                    "ns": ["openmicroscopy.org/omero/bulk_annotations"],
                    "label": "Others"
                }
            }
        ]
    ))
    django.setup()
