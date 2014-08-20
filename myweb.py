#encoding: utf-8
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import hashlib

import pymongo

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [(r"/", MainHandler),
					(r"/regist", RegistHandler),
					(r"/login", LoginHandler),
					(r"/exit", LogoutHandler)]
		settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "templates"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            cookie_secret = "g90egjg3HJIHHhjkh432joiHIOH/Vo=",
            xsrf_cookies = True,
            ui_modules = {'Login':LoginModule},
            debug=True,
        )
		conn = pymongo.Connection("localhost", 27017)
		self.db = conn.companydb
		tornado.web.Application.__init__(self, handlers, **settings)

class MainHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		staff_cookie = self.get_secure_cookie('staff')
		basic = self.application.db.basic
		info = basic.find_one()
		staff = self.application.db.staff
		staffs = staff.find()
		self.render("index.html",basic = info,staffs = staffs,user = staff_cookie)

class LoginHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		staffs = self.application.db.staff
		pw = self.get_argument('user_pw')
		remote_ip = self.request.remote_ip
		staff = staffs.find_one({'user_id':self.get_argument('user_id'),'user_pw':hashlib.new('md5',pw).hexdigest(),\
			'user_ip':remote_ip})
		if staff:
			self.set_secure_cookie('staff',staff)
			self.render('/')
		else:
			self.write("编号或密码输入错误/IP地址不符。")

class LogoutHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.clear_cookie("user")
		self.redirect("/")

class RegistHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.render("regist.html")

	@tornado.web.asynchronous
	def post(self):
		db = self.application.db.staff
		db.insert({'user_id':self.get_argument('user_id'),'user_name':self.get_argument('user_name'),\
			'user_ip':self.get_argument('user_ip'),'user_pw':hashlib.new('md5',self.get_argument('user_pw')).hexdigest()})
		self.redirect('/')

class LoginModule(tornado.web.UIModule):
	def render(self,staff):
		return self.render_string('modules/login.html',staff = staff)


if __name__ == "__main__":
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
