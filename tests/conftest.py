import os
import json
import django
import pytest

from django.conf import settings
from omero_mapr.utils import config_list_to_dict

from omero_mapr.testlib import IMaprTest

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


@pytest.fixture
def itest(request):
    """
    Returns a new L{weblibrary.IMaprTest} instance. With attached
    finalizer so that pytest will clean it up.
    """
    IMaprTest.setup_class()

    def finalizer():
        IMaprTest.teardown_class()
    request.addfinalizer(finalizer)
    return IMaprTest()


@pytest.fixture(scope="session")
def imaprtest(request):
    """
    Returns a new L{weblibrary.IMaprTest} instance. With attached
    finalizer so that pytest will clean it up.
    """
    IMaprTest.setup_class()

    def finalizer():
        IMaprTest.teardown_class()
    request.addfinalizer(finalizer)

    imt = IMaprTest()
    csv = os.path.join(
        os.path.dirname(__file__), 'integration',
        'bulk_to_map_annotation_context_ns.csv')
    cfg = os.path.join(
        os.path.dirname(__file__), 'integration',
        'bulk_to_map_annotation_context.yml')
    imt.populate_data(csv, cfg)
    return imt
