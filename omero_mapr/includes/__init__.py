
# The webclient looks in app/includes module for "right_panel_title"
# to add custom html to the right panel

def right_panel_title(**kwargs):

    conn = kwargs.get("conn")
    c_id = kwargs.get("c_id")
    c_type = kwargs.get("c_type")

    # We only want to handle Projects or Screens
    if c_type not in ("project", "screen"):
        return ""

    title = None
    if conn is not None and c_id is not None:
        for link in conn.getAnnotationLinks(c_type, [c_id]):
            ann = link.getAnnotation()
            if "MapAnnotationI" in str(ann.OMERO_TYPE):
                for kvp in ann.getValue():
                    if kvp[0] == "Publication Title":
                        title = kvp[1]
                        break

    if title is not None:
        return "<h1>%s</h1>" % title
    return ""
