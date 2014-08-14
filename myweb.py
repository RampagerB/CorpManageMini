import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

import pymongo

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [(r"/",MainHandler)]
		settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
		conn = pymongo.Connection("localhost", 27017)
		self.db = conn.companydb
		tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		basic = self.application.db.basic
		info = basic.find_one()
		self.render("index.html",basic = info)

class RegistHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("regist.html")

if __name__ == "__main__":
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
