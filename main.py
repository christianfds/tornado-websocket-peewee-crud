import asyncio
import tornado.escape
import tornado.ioloop
import tornado.locks
import tornado.web
import tornado.websocket
import os
import time
import uuid
import json

from playhouse.shortcuts import model_to_dict
from datetime import date
from tornado.options import define, options, parse_command_line

from models import *

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        if db.is_closed():
            db.connect()
        return super(BaseHandler, self).prepare()
    
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        
    def on_finish(self):
        if not db.is_closed():
            db.close()
        return super(BaseHandler, self).on_finish()


clients = {}


class WSUpdatesHandler(tornado.websocket.WebSocketHandler):

    # def __init__(self, request, **kwarg):
    #     super.__init__(self, kwargs)

    def check_origin(self, origin):
        return True

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def open(self):
        self.client_id = str(self.get_secure_cookie("uuid"))
        clients[self.client_id] = self

        msg = {
            'type': 'UPDATE',
            'quantity': count_produto_carrinho(self.client_id)
        }
        self.write_message(json.dumps(msg))

    def on_close(self):
        clients.pop(self.client_id, None)

    def on_message(self):
        self.send_message('oi')

    def send_message(self, message):
        if clients[self.client_id]:
            clients[self.client_id].write_message(message)


def send_ws_message(client_id, message):
    if client_id == "ALL":
        for client in clients:
            client.write_message(message)
    elif client_id in clients:
        clients[str(client_id)].write_message(message)


class ShoppingCartListHandler(BaseHandler):
    def get(self):
        v = [p for p in get_produtos_carrinho(self.get_secure_cookie('uuid')).dicts()]

        self.write(json.dumps(v))


class ShoppingCartAddHandler(BaseHandler):
    def post(self):
        client_id = str(self.get_secure_cookie('uuid'))
        add_produto_carrinho(
            client_id, self.get_body_argument('produtoid'))

        msg = {
            'type': 'UPDATE',
            'quantity': count_produto_carrinho(client_id)
        }

        send_ws_message(client_id, msg)

        self.write(json.dumps({
            'message': 'SUCCESS'
        }))


class GetProdutosHandler(BaseHandler):
    async def get(self):
        with db.atomic():
            v = [p for p in Produto.select().dicts()]

        self.write(json.dumps(v))


class MainHandler(BaseHandler):
    def get(self):
        if not self.get_secure_cookie("uuid"):
            self.set_secure_cookie("uuid", str(uuid.uuid4()))

        self.render("index.html")


if __name__ == "__main__":
    create_tables()

    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/cart/updates", WSUpdatesHandler),
            (r"/produto/add", ShoppingCartAddHandler),
            (r"/produto/cart", ShoppingCartListHandler),
            (r"/produtos", GetProdutosHandler),
        ],
        cookie_secret="Batata",
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=False,
        debug=options.debug,
    )
    app.listen(int(os.environ.get("PORT", options.port)))
    tornado.ioloop.IOLoop.current().start()
