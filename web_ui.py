#!/usr/bin/env python

import os
import time
import json
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
import traceback


ins = None

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")


class AllDataHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        data = {}
        try:
            t = ins.get_time()
            ax, ay, az, gx, gy, gz, mx, my, mz = ins.get_all_sensor_data()
            qx, qy, qz, qw = ins.get_quaternion()
            vx, vy, vz = ins.get_velocity()
            rx, ry, rz = ins.get_position()

            data["time"] = ins.get_time()
            data["result"] = "successed"
            data["acceleration"] = [ax, ay, az]
            data["angular_rate"] = [gx, gy, gz]
            data["magnetic"] = [mx, my, mz]
            data["quaternion"] = [qx, qy, qz, qw]
            data["velocity"] = [vx, vy, vz]
            data["position"] = [rx, ry, rz]
        except Exception:
            data["result"] = "failed"
            data["message"] = "no data available."

        self.write(json.dumps(data, ensure_ascii=False))
        self.finish()


class ResetDataHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        ins.reset_data()
        data = {'result': 'successed'}
        self.write(json.dumps(data, ensure_ascii=False))
        self.finish()


app = tornado.web.Application([
    (r"/", MainHandler),
    (r"/alldata", AllDataHandler),
    (r"/resetdata", ResetDataHandler)],
    template_path=os.path.join(os.getcwd(),  "templates"),
    static_path=os.path.join(os.getcwd(),  "static"),
)


def start(_ins):
    port = 8080
    global ins
    ins = _ins
    app.listen(port)
    print('Start web server on port %d' % port)
    tornado.ioloop.IOLoop.instance().start()
