## MAPR URLs

----

| URL                          | METHOD | URL PARAMS                                                                            | QUERY STRING                                                                        | Success Response | Error Response:                                   | Sample Call:                                                                                                                                                                                                                                                                                                                                                                                              |
|------------------------------|--------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|------------------|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/webclient/`                | GET    |                                                                                       | `show=<type>-<value>`                                                               | 302 redirect     |                                                   | `/webclient/?show=gene-CDC20`                                                                                                                                                                                                                                                                                                                                                                             |
| `/mapr/<type>/`                   | GET    | `type=(gene|phenotype|sirna|compound|organism)`                                       | `value=<value>` `query=(true|false)` `default:false`                                | 200 HTML         |                                                   | `/mapr/gene/?value=CDC20` `/mapr/organism/?value=CDC2&query=true`                                                                                                                                                                                                                                                                                                                  |



**Attribute URL**
----

  Attribute URL, Attributes are preconfigured in application settings https://github.com/ome/omero-mapr/blob/master/mapr/mapr_settings.py or can be altered by changing omero config`omeroweb.mapr.config`

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

  `http://idr-demo.openmicroscopy.org/mapr/gene/?value=CDC20`
  `http://idr-demo.openmicroscopy.org/mapr/gene/?value=CDC2&query=true`
 
 
 ## MAPR JSON API

 ----


 | URL                          | METHOD | URL PARAMS                                                                            | QUERY STRING                                                                        | Success Response | Error Response:                                   | Sample Call:                                                                                                                                                                                                                                                                                                                                                                                              |
 |------------------------------|--------|---------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|------------------|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
 | `/mapr/api/<type>/count/`         | GET    | `type=(gene|phenotype|sirna|compound|organism)`                                       | `value=<value>` `query=(true|false)` `default:false`                                | 200 JSON         | 400 Invalid parameter value 400 ApiUsageException | `/api/gene/count/?value=CDC20` `/api/gene/count/?value=CDC20query=true`                                                                                                                                                                                                                                                                                                                                   |
 | `/mapr/api/<type>/`               | GET    | `type=(gene|phenotype|sirna|compound|organism)`                                       | `id=<value|id>` `orphaned=(true|false)` `value=<value>`                             | 200 JSON         | 400 Invalid parameter value 400 ApiUsageException | `/api/gene/?value=CDC20&orphaned=true` get value and children count `/api/gene/?value=CDC20&query=true&orphaned=true` get value matching `%value%` pattern and children count and image count `/api/gene/?id=CDC20` returns list of screens and/or projects for given gene ID `/api/gene/?value=CDC20&query=true` returns list of screens and/or projects for matching `%value%` pattern with exact value |
 | `/mapr/api/<type>/<containers>/`  | GET    | `type=(gene|phenotype|sirna|compound|organism)` `containers=(plates|datasets|images)` | `value=<value>` `id=<parent_id>` if `containers=images` then `node=(plate|dataset)` | 200 JSON         | 400 Invalid parameter value 400 ApiUsageException | `api/gene/plates/?value=CDC20&query=true&id=1202` return list of plates/datasets in screen/project for given parent_id` and value` /api/gene/images/?value=991&query=true&node=plate&id=1692 return list of images (Fileset IDs) for a give `parent_id` and matching `%value%` pattern with exact value                                                                                                   |
 | `/mapr/api/annotations/<type>/`   | GET    | `type=(gene|phenotype|sirna|compound|organism)`                                       | `type=map` `map=<value>` or `(screen|plate|project|dataset|image)=<id>`             | 200 JSON         | 400 Invalid parameter value400 ApiUsageException  | return map annotations containing given value (case sensitive)                                                                                                                                                                                                                                                                                                                                            |
 | `/mapr/api/gene/paths_to_object/` | GET    |                                                                                       | `map.value=`                                                                        | 200 JSON         |                                                   | find hierarchies for a given value (case sensitive) - in case we will provide multiple users or groups                                                                                                                                                                                                                                                                                                    |
 | `/mapr/autocomplete/<type>/` | GET    | `type=(gene|phenotype|sirna|compound|organism)`                                       | `value=<value>` `query=true`                                                        | 200 JSON         |                                                   | find keywords for matching `%value%` pattern                                                                                                                                                                                                                                                                                                                                                              |
 