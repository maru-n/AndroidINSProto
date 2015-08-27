#!/usr/bin/env python

import os
import time
import json
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback


ins = None

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")


class AllDataHandler(tornado.websocket.WebSocketHandler):
    @tornado.web.asynchronous
    def get(self):
        data = {}
        try:
            data["time"] = ins.get_time()
            ax, ay, az, gx, gy, gz, mx, my, mz = ins.get_all_sensor_data()
            data["result"] = "successed"
            data["acceleration"] = [ax, ay, az]
            data["angular_rate"] = [gx, gy, gz]
            data["magnetic"] = [mx, my, mz]
            x, y, z, w = ins.get_quaternion();
            data["quaternion"] = [x, y, z, w]
        except Exception:
            data["result"] = "failed"
            data["message"] = "no data available."
            # print(traceback.format_exc())
        self.write(json.dumps(data, ensure_ascii=False))
        self.finish()


app = tornado.web.Application([
    (r"/", MainHandler),
    (r"/alldata", AllDataHandler)],
    template_path=os.path.join(os.getcwd(),  "templates"),
    static_path=os.path.join(os.getcwd(),  "static"),
)


def start(_ins):
    global ins
    ins = _ins
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
