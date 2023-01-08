from flasgger import Swagger
from flask import Blueprint, Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from redis import Redis
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.config import app_config


app = Flask(__name__)


def configure_tracer() -> None:
    resource = Resource(attributes={
        SERVICE_NAME: 'auth-service'
    })
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name='tracing',
                agent_port=6831,
            )
        )
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


# @app.before_request
# def before_request():
#     request_id = request.headers.get('X-Request-Id')
#     if not request_id:
#         raise RuntimeError('request id is required')


if app_config.ENABLE_TRACER:
    configure_tracer()
    FlaskInstrumentor().instrument_app(app)


redis_uri = f"redis://{app_config.REDIS_HOST}:{app_config.REDIS_PORT}"
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per minute"],
    storage_uri=redis_uri
)


swagger = Swagger(
    app,
    template={
        "swagger": "2.0",
        "info": {
            "title": "Auth service",
            "version": "1.0",
        },
        "consumes": [
            "application/json",
        ],
        "produces": [
            "application/json",
        ],
    },
)

app.config["SECRET_KEY"] = app_config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = \
    f"postgresql://{app_config.DB_USER}:{app_config.DB_PASSWORD}@{app_config.DB_AUTH_HOST}:{app_config.DB_AUTH_PORT}" \
    f"/{app_config.DB_AUTH_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SWAGGER"] = {
    "title": "Swagger JWT Authentiation App",
    "uiversion": 3,
}
db = SQLAlchemy(app)
migrate = Migrate(app, db)

cache = Redis(host=app_config.REDIS_HOST, port=app_config.REDIS_PORT, decode_responses=True)

urls = Blueprint("urls", __name__)
usersbp = Blueprint("users", __name__)

limiter.limit('1000 per minute')(urls)
limiter.limit('10 per second')(usersbp)

# Инициализируем точки API до регистрации blueprint
import api.v1.auth
import api.v1.auth_history
import api.v1.oauth
import api.v1.permission
import api.v1.refresh_token
import api.v1.role
import api.v1.user
from app.commands import create_partition_year, create_superuser

app.register_blueprint(urls, url_prefix="/api/v1/auth")
app.register_blueprint(usersbp)
