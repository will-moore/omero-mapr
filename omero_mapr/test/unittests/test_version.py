import pytest

from omero_mapr.utils.version import get_version


class TestUtil(object):

    """
    Tests various util methods
    """

    @pytest.mark.parametrize('version', [
        ('0.0', (0, 0, 0)),
        ('0.5.20', (0, 5, 20)),
        ('1.0.20', (1, 0, 20)),
        ('1.0', (1, 0, 0)),
        ('0.1.2dev', (0, 1, 2, 'dev')),
        ('1.2.3rc', (1, 2, 3, 'rc')),
        ('1.0rc', (1, 0, 0, 'rc'))
    ])
    def test_version(self, version):
        v = version[1]
        assert version[0] == get_version(v)
