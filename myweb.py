#encoding: utf-8
import os.path
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import hashlib

import pymongo

from bson.json_util import dumps,loads

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
	def __init__(self):
		handlers = [(r"/", MainHandler),
					(r"/regist", RegistHandler),
					(r"/login", LoginHandler),
					(r"/changepw/(\w*)", ChangePwHandler),
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
		staff = self.application.db.staff
		staffs = staff.find()
		self.render("index.html",staffs = staffs,user = staff_cookie)

class LoginHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def post(self):
		staffs = self.application.db.staff
		users = staffs.find()
		uid = self.get_argument('user_id')
		pw = self.get_argument('user_pw')
		staff = staffs.find_one({'user_id':uid,'user_pw':hashlib.new('md5',pw).hexdigest()})
		if staff:
			staff = dumps(staff)
			self.set_secure_cookie('staff',staff)
			self.render('index.html',user=staff,staffs=users)
			self.finish()
		else:
			self.write("编号或密码输入错误")
			self.finish()

class LogoutHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self):
		self.clear_cookie("staff")
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
		if staff:
			staff = loads(staff)
		return self.render_string('modules/login.html',user = staff)

class ChangePwHandler(tornado.web.RequestHandler):
	@tornado.web.asynchronous
	def get(self,user_id):
		self.render("changepw.html",user_id=user_id)

	@tornado.web.asynchronous
	def post(self):
		user = self.get_secure_cookie("staff")
		db = self.application.db.staff
		db.insert({'user_id':self.get_argument('user_id'),'user_name':self.get_argument('user_name'),\
			'user_ip':self.get_argument('user_ip'),'user_pw':hashlib.new('md5',self.get_argument('user_pw')).hexdigest()})
		self.redirect('/')

if __name__ == "__main__":
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
