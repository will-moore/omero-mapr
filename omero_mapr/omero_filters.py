from omero.rtypes import rint
from django.http import JsonResponse
import json
from omero.sys import ParametersI
from omero_parade.utils import get_image_ids

from mapr_settings import mapr_settings


def get_filters(request, conn):
    return ["mapr_%s" % key for key in mapr_settings.CONFIG]


def get_script(request, script_name, conn):
    """Return a JS function to filter images by various params."""
    dataset_id = request.GET.get('dataset')
    plate_id = request.GET.get('plate')
    field_id = request.GET.get('field')
    if plate_id and field_id:
        img_ids = get_image_ids(conn, plate_id, field_id)
    elif dataset_id:
        img_ids = [i.id for i in conn.getObjects('Image', opts={'dataset': dataset_id})]
    query_service = conn.getQueryService()

    if script_name.startswith('mapr_'):
        mapr_key = script_name.replace('mapr_', '')

        # Get all map annotations with correct namespace...

        # OrderedDict([(u'gene', {u'default': [u'Gene Symbol'], u'all': [u'Gene Symbol', u'Gene Identifier'], u'ns': [u'openmicroscopy.org/mapr/gene'], u'label': u'Gene'})])
        mapr_dict = mapr_settings.CONFIG[mapr_key]
        ns = mapr_dict['ns'][0]
        all_keys = mapr_dict['all']
        print all_keys, ns

        params = ParametersI()
        params.addIds(img_ids)
        params.addString('ns', ns)
        query = """select oal from ImageAnnotationLink as oal
            join fetch oal.details.owner
            left outer join fetch oal.child as ch
            left outer join fetch oal.parent as pa
            where pa.id in (:ids)
            and ch.ns=:ns"""
        links = query_service.findAllByQuery(query, params, conn.SERVICE_OPTS)

        # For each image, we want to add {key: value} for keys specified by mapr
        values = {}
        for l in links:
            d = {}
            for kv in l.child.getMapValue():
                d[kv.name] = kv.value
            values[l.parent.id.val] = d


        # Return a JS function that will be passed an object e.g. {'type': 'Image', 'id': 1}
        # and should return true or false
        f = """(function filter(data, params) {
            var values = %s;
            if (params.query === '') return true;
            var map_ann = values[data.id];
            var search_values = '';
            if (params.mapr_key === 'All') {
                search_values = Object.values(map_ann).join(" ");
            } else {
                search_values = map_ann[params.mapr_key]
            }
            return (search_values.indexOf(params.query) > -1);
        })
        """ % json.dumps(values)

        filter_by = ['All']
        filter_by.extend(all_keys)

        filter_params = [{'name': 'mapr_key',
                          'type': 'text',
                          'values': filter_by,
                          'default': 'All',
                          },
                          {'name': 'query',
                          'type': 'text',
                          'default': '',
                          }]
        return JsonResponse(
            {
                'f': f,
                'params': filter_params,
            })

    