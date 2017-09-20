# MAPR API

## Attribute URL

Top level Attribute URL. Attributes are preconfigured in application settings https://github.com/ome/omero-mapr/blob/master/omero_mapr/mapr_settings.py
or can be altered by changing omero config `omero.web.mapr.config`

| URL                          | METHOD | URL PARAMS                                                                            | QUERY STRING                                                                        | Success Response | Error Response:                                   | Sample Call:                                                                                                                                                                                                                                                                                                                                                                                              |
|------------------------------|--------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|------------------|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/webclient/`*              | GET    |                                                                                       | `show=<type>-<value>`                                                               | 302 redirect     |                                                   | `/webclient/?show=gene-CDC20`                                                                                                                                                                                                                                                                                                                                                                             |
| `/mapr/<type>/`                   | GET    | <code>type=(gene&#124;phenotype&#124;sirna&#124;compound&#124;organism)</code>                                       | `value=<value>` <code>query=(true&#124;false)</code> `default:false`                                | 200 HTML         |                                                   | `/mapr/gene/?value=CDC20` `/mapr/organism/?value=CDC2&query=true`                                                                                                                                                                                                                                                                                                                  |

**Show URL***
----

Extention to OMERO.web "showing" plugin

* **URL**

  `/webclient/`

* **Method:**

  `GET`

*  **QUERY STRING**

   **Required:**

   `show=[string]`

* **Success Response:**

  * **Code:** 302 <br />

* **Sample Call:**

  `http://idr.openmicroscopy.org/webclient/?show=gene-CDC20`

*) Default alias for handling particular links and recognizing objects in the
OMERO.web tree view.


**Attribute URL**
----

* **URL**

  `/mapr/<type>/`

* **Method:**

  `GET`

*  **URL Params**

   **Required:**

   `type=[gene|phenotype|sirna|compound|organism]`

*  **QUERY STRING**

   **Required:**

   `value=[string]`

   **Optional:**

   `query=[boolean] default:false`

* **Success Response:**

  * **Code:** 200 <br />
  * **Content:** `HTML`

* **Sample Call:**

  `http://idr.openmicroscopy.org/mapr/gene/?value=CDC20`

  `http://idr.openmicroscopy.org/mapr/gene/?value=CDC2&query=true`


## MAPR JSON API

| URL                          | METHOD | URL PARAMS                                                                            | QUERY STRING                                                                        | Success Response | Error Response:                                   | Sample Call:                                                                                                                                                                                                                                                                                                                                                                                              |
|------------------------------|--------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|------------------|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/mapr/api/<type>/count/`         | GET    | <code>type=(gene&#124;phenotype&#124;sirna&#124;compound&#124;organism)</code>                                       | `value=<value>` <code>query=(true&#124;false)</code> `default:false`                                | 200 JSON         | 400 Invalid parameter value 400 ApiUsageException | `/api/gene/count/?value=CDC20` `/api/gene/count/?value=CDC20query=true`                                                                                                                                                                                                                                                                                                                                   |
| `/mapr/api/<type>/`               | GET    | <code>type=(gene&#124;phenotype&#124;sirna&#124;compound&#124;organism)</code>                                       | <code>id=<value&#124;id></code> <code>orphaned=(true&#124;false)</code> `value=<value>`                             | 200 JSON         | 400 Invalid parameter value 400 ApiUsageException | `/api/gene/?value=CDC20&orphaned=true` get value and children count `/api/gene/?value=CDC20&query=true&orphaned=true` get value matching `%value%` pattern and children count and image count `/api/gene/?id=CDC20` returns list of screens and/or projects for given gene ID `/api/gene/?value=CDC20&query=true` returns list of screens and/or projects for matching `%value%` pattern with exact value |
| `/mapr/api/<type>/<containers>/`  | GET    | <code>type=(gene&#124;phenotype&#124;sirna&#124;compound&#124;organism)</code> <code>containers=(plates&#124;datasets&#124;images)</code> | `value=<value>` `id=<parent_id>` if `containers=images` then <code>node=(plate&#124;dataset)</code> | 200 JSON         | 400 Invalid parameter value 400 ApiUsageException | `api/gene/plates/?value=CDC20&query=true&id=1202` return list of plates/datasets in screen/project for given parent_id` and `value` `/api/gene/images/?value=991&query=true&node=plate&id=1692` return list of images (Fileset IDs) for a give `parent_id` and matching `%value%` pattern with exact value                                                                                                   |
| `/mapr/api/annotations/<type>/`   | GET    | <code>type=(gene&#124;phenotype&#124;sirna&#124;compound&#124;organism)</code>                                       | `type=map` `map=<value>` or <code>(screen&#124;plate&#124;project&#124;dataset&#124;image)=<id></code>            | 200 JSON         | 400 Invalid parameter value400 ApiUsageException  | return map annotations containing given value (case sensitive)                                                                                                                                                                                                                                                                                                                                            |
| `/mapr/api/gene/paths_to_object/` | GET    |                                                                                       | `map.value=`                                                                        | 200 JSON         |                                                   | find hierarchies for a given value (case sensitive) - in case we will provide multiple users or groups                                                                                                                                                                                                                                                                                                    |
| `/mapr/autocomplete/<type>/` | GET    | <code>type=(gene&#124;phenotype&#124;sirna&#124;compound&#124;organism)</code>                                       | `value=<value>` `query=true`                                                        | 200 JSON         |                                                   | find keywords for matching `%value%` pattern                                                                                                                                                                                                                                                                                                                                                              |


### Example script

OMERO.web uses default session backend authentication scheme for authentication.

Example script begins by creating HTTP session using Requests:

```
import requests

INDEX_PAGE = "http://idr.openmicroscopy.org/webclient/?experimenter=-1"

# create http session
with requests.Session() as session:
    request = requests.Request('GET', INDEX_PAGE)
    prepped = session.prepare_request(request)
    response = session.send(prepped)
    if response.status_code != 200:
        response.raise_for_status()
```

get Screens that are annotated with gene:

```
SCREENS_PROJECTS_URL = "http://idr.openmicroscopy.org/mapr/api/{key}/?value={value}"

qs = {'key': 'gene', 'value': 'CDC20'}
url = SCREENS_PROJECTS_URL.format(**qs)
for s in session.get(url).json()['screens']:
    screen_id = s['id']
```

get Plates in Screen that are annotated with gene:

```
PLATES_URL = "http://idr.openmicroscopy.org/mapr/api/{key}/plates/?value={value}&id={screen_id}"

qs = {'key': 'gene', 'value': 'CDC20', 'screen_id': screen_id}
url = PLATES_URL.format(**qs)
for p in session.get(url).json()['plates']:
    plate_id = p['id']
````

get Images in Plate that are annotated with gene:

```
IMAGES_URL = "http://idr.openmicroscopy.org/mapr/api/{key}/images/?value={value}&node={parent_type}&id={parent_id}"

IMAGE_URL = "http://idr.openmicroscopy.org/webclient/?show=image-{image_id}"
IMAGE_VIEWER = "http://idr.openmicroscopy.org/webclient/img_detail/{image_id}/"
THUMBNAIL_URL = "http://idr.openmicroscopy.org/webclient/render_thumbnail/{image_id}/"
ATTRIBUTES_URL = "http://idr.openmicroscopy.org/webclient/api/annotations/?type=map&image={image_id}"

qs = {'key': 'gene', 'value': 'CDC20', 'parent_type': 'plate', 'parent_id': plate_id}
url = IMAGES_URL.format(**qs)
for i in session.get(url).json()['images']:
    image_id = i['id']
    print "Image link:", IMAGE_URL.format(**{'image_id': image_id})
    print "Image viewer link:", IMAGE_VIEWER.format(**{'image_id': image_id})
    print 'Thumbnail URL:', THUMBNAIL_URL.format(**{'image_id': image_id})
    url = ATTRIBUTES_URL.format(**{'image_id': image_id})
    for a in session.get(_url).json()['annotations']:
        print 'Annotaitons:'
        print a['values']
```

example output:

```
Image link: http://idr.openmicroscopy.org/webclient/?show=image-124486
Image viewer link: http://idr.openmicroscopy.org/webclient/img_detail/124486/
Thumbnail URL: http://idr.openmicroscopy.org/webclient/render_thumbnail/124486/
Annotaitons:
[[u'Gene Identifier', u'YGL116W'], [u'Gene Identifier URL', u'http://www.yeastgenome.org/locus/YGL116W/overview'], [u'Gene Symbol', u'CDC20']]
Annotaitons:
[[u'Organism', u'Saccharomyces cerevisiae']]
Annotaitons:
[[u'Phenotype', u'GFP localization: cytosol'], [u'Phenotype Term Name', u'protein localized in cytosol phenotype'], [u'Phenotype Term Accession', u'CMPO_0000393'], [u'Phenotype Term Accession URL', u'http://www.ebi.ac.uk/cmpo/CMPO_0000393']]
Annotaitons:
[[u'Phenotype', u'GFP localization: nucleus'], [u'Phenotype Term Name', u'protein localized in nucleus phenotype'], [u'Phenotype Term Accession', u'CMPO_0000398'], [u'Phenotype Term Accession URL', u'http://www.ebi.ac.uk/cmpo/CMPO_0000398']]
Annotaitons:
[[u'Strain', u'Y6545'], [u'Environmental Stress', u'dithiothreitol'], [u'Channels', u'H2B-mCherry:cytosol;GFP:tagged protein;bright field/transmitted:cell '], [u'Has Phenotype', u'yes'], [u'Phenotype Annotation Level', u'experimental condition and gene']]
````
