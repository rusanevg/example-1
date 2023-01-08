from gevent import monkey
monkey.patch_all()

from gevent.pywsgi import WSGIServer

from app.flask_app import app


def main():
    http_server = WSGIServer(("", 5000), app)
    http_server.serve_forever()


if __name__ == "__main__":
    main()
