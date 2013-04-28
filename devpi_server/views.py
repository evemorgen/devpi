
from py.xml import html
from devpi_server.types import lazydecorator
from bottle import response, request

def simple_html_body(title, bodytags):
    return html.html(
        html.head(
            html.title(title)
        ),
        html.body(
            html.h1(title),
            *bodytags
        )
    )

route = lazydecorator()

class PyPIView:
    def __init__(self, extdb):
        self.extdb = extdb

    @route("/ext/pypi/<projectname>")
    @route("/ext/pypi/<projectname>/")
    def extpypi_simple(self, projectname):
        # we only serve absolute links so we don't care about the
        # route's slash
        result = self.extdb.getreleaselinks(projectname)
        if isinstance(result, int):
            raise BadGateway()
        links = []
        for entry in result:
            href = "/pkg/" + entry.relpath
            if entry.eggfragment:
                href += "#egg=%s" % entry.eggfragment
            elif entry.md5:
                href += "#md5=%s" % entry.md5
            links.append((href, entry.basename))

        # construct html
        body = []
        for entry in links:
            body.append(html.a(entry[1], href=entry[0]))
            body.append(html.br())
        return simple_html_body("links for %s" % projectname, body).unicode()

class PkgView:
    def __init__(self, filestore, httpget):
        self.filestore = filestore
        self.httpget = httpget

    @route("/pkg/<relpath:re:.*>")
    def pkgserv(self, relpath):
        headers, itercontent = self.filestore.iterfile(relpath, self.httpget)
        response.content_type = headers["content-type"]
        if "content-length" in headers:
            response.content_length = headers["content-length"]
        for x in itercontent:
            yield x