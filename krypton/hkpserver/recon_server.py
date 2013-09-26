
import sys

try:
    import tornado.ioloop
    import tornado.web
except ImportError:
    sys.stderr.write("Looks like you have tornado not installed. (apt-get install python-tornado)")
    sys.exit(1)


class ReconController(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        print args
        print kwargs
        print self.request

    def post(self, *args, **kwargs):
        self.get(args,kwargs)

if __name__ == "__main__":


    application = tornado.web.Application([
        (r"/", ReconController),
    ])

if __name__ == "__main__":
    application.listen(11370)
    tornado.ioloop.IOLoop.instance().start()