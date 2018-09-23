import os
import sys

from jinja2 import Environment, FileSystemLoader
from tornado import web, httpserver
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.log import app_log, access_log, gen_log
from traitlets import (
    Dict, )
from traitlets.config import Application, logging

from .opencv_service.opencv_service import OpencvService
from .handlers.image_handler import ImageHandler

current_dir = os.path.dirname(__file__)
common_aliases = {
    'log-level': 'Application.log_level',
}
aliases = {
    'encodings': 'OpencvService.encodings',
    'images': 'OpencvService.images'
}
aliases.update(common_aliases)
flags = {}


class ImageTaggerServer(Application):

    aliases = Dict(aliases)
    flags = Dict(flags)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.io_loop = None
        self.tornado_application = None
        self.http_server = None
        self.handlers = []
        self.tornado_settings = {}

    def initialize(self, *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.init_logging()

        self.log.info("=> Initializing")

        # => OpenCv service
        opencv_service = OpencvService()

        # => Tornado settings
        self.tornado_settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "images"),
            "static_url_prefix": "/statics/",
            "opencv_service": opencv_service
        }
        # => Tornado handlers
        self.handlers.append((r"/image/(\d+)/?(\d+)?", ImageHandler))

        # => Jinja2 templating engine
        self.init_jinja2_engine()

        # => Tornado application
        self.tornado_application = web.Application(self.handlers, **self.tornado_settings)

    def init_jinja2_engine(self):
        jinja_options = dict(autoescape=True, )
        loader = FileSystemLoader(os.path.join(current_dir, "templates"))
        jinja_env = Environment(loader=loader, **jinja_options)
        self.tornado_settings.update(dict(jinja2_env=jinja_env))

    def init_logging(self):
        self.log.propagate = False
        self.log_level = logging.INFO

        # disable curl debug, which is TOO MUCH
        logging.getLogger('tornado.curl_httpclient').setLevel(logging.INFO)
        for log in (app_log, access_log, gen_log):
            # ensure all log statements identify the application they come from
            log.name = self.log.name
        logger = logging.getLogger('tornado')
        logger.propagate = True
        logger.parent = self.log
        logger.setLevel(self.log.level)

    def start(self):
        super().start()
        self.log.info("=> Starting server")

        # => Tornado http server
        self.io_loop = IOLoop.current()
        self.http_server = HTTPServer(self.tornado_application)
        self.http_server.listen(8080, address="0.0.0.0")
        self.log.info("API listening on %s", "0.0.0.0:8080")

    @classmethod
    def instantiate(cls, argv):

        self = cls.instance()
        loop = IOLoop.current()
        self.initialize(argv)
        self.start()
        try:
            loop.start()
        except KeyboardInterrupt:
            print("\nInterrupted")

        httpserver.HTTPServer(self.tornado_application, xheaders=True)


if __name__ == "__main__":
    ImageTaggerServer.instantiate(sys.argv[1:])
    # main(["-e", "faces_db/faces.db", "-i", "images"] if len(sys.argv[1:]) == 0 else sys.argv[1:])
