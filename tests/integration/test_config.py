import pytest

from django.core.urlresolvers import reverse, NoReverseMatch

from omeroweb.testlib import IWebTest, _get_response


@pytest.fixture
def empty_settings(settings):
    settings.MAPR_CONFIG = {}


class TestMapr(IWebTest):

    def test_settings(self, settings):
        assert len(settings.MAPR_CONFIG.keys()) > 0
        for menu in settings.MAPR_CONFIG.keys():
            request_url = reverse("maprindex_%s" % menu)
            _get_response(self.django_client, request_url, {}, status_code=200)

    @pytest.mark.xfail(raises=StopIteration)
    def test_empty_settings(self, empty_settings):
        # test empty config
        reverse("maprindex")

    @pytest.mark.parametrize('menu', ['foo', '', 'mygenes'])
    def test_bad_settings(self, settings, menu):
        assert menu not in settings.MAPR_CONFIG.keys()
        with pytest.raises(NoReverseMatch) as excinfo:
            request_url = reverse("maprindex_%s" % menu)
            _get_response(self.django_client, request_url, {}, status_code=200)
        regx = r"Reverse for 'maprindex_%s'.*" % menu
        assert excinfo.match(regx)
