from tornado.web import RequestHandler


class BaseHandler(RequestHandler):

    def data_received(self, chunk):
        pass

    # ---------------------------------------------------------------
    # template rendering
    # ---------------------------------------------------------------

    @property
    def template_namespace(self):
        ns = dict()
        if 'template_vars' in self.settings:
            ns.update(self.settings['template_vars'])

        return ns

    def get_template(self, name):
        """Return the jinja template object for a given name"""

        return self.settings['jinja2_env'].get_template(name)

    def render_template(self, name, **ns):
        template_ns = {}
        template_ns.update(self.template_namespace)
        template_ns.update(ns)
        template = self.get_template(name)

        return template.render(**template_ns)
