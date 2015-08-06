#!/usr/bin/env python

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.ioloop import PeriodicCallback
from tornado.options import define, options, parse_command_line

from data_receiver import DataReceiver


data_receiver = None


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("index.html")


class MainWSHandler(tornado.websocket.WebSocketHandler):

    def open(self):
        self.data_receiver = DataReceiver()
        self.callback = PeriodicCallback(self._send_message, 100)
        self.callback.start()

    def on_message(self, message):
        print(message)

    def _send_message(self):
        try:
            ax, ay, az, gx, gy, gz, mx, my, mz = data_receiver.fetch_all_data()
            msg = ''
            msg += 'accel(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (ax, ay, az)
            msg += 'gyro(x:% 9.5f y:% 9.5f z:% 9.5f)  ' % (gx, gy, gz)
            msg += 'mag(x:% 10.5f y:% 10.5f z:% 10.5f)' % (mx, my, mz)
        except Exception as e:
            msg = "no data available."
            print(e)
        finally:
            self.write_message(msg)

    def on_close(self):
        self.callback.stop()
        print("WebSocket closed")

define("port", default=8080, help="run on the given port", type=int)
app = tornado.web.Application([
    (r"/", MainHandler),
    (r"/ws", MainWSHandler),
])


def start(_data_receiver):
    global data_receiver
    data_receiver = _data_receiver
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
