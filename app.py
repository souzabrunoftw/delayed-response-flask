import sys
from datetime import datetime
import logging
import os
import random
from time import sleep

import requests
import tracer
from flask import Flask  # import flask
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from pythonjsonlogger import jsonlogger

OPEN_TELEMETRY_ENDPOINT_HOST = os.getenv("OPEN_TELEMETRY_ENDPOINT_HOST")
OPEN_TELEMETRY_ENDPOINT_PORT = os.getenv("OPEN_TELEMETRY_ENDPOINT_PORT")

mylogger = logging.getLogger()

logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
mylogger.addHandler(logHandler)
mylogger.setLevel(logging.INFO)

app = Flask(__name__)  # create an app instance


provider = TracerProvider()

provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="{host}:{port}".format(host=OPEN_TELEMETRY_ENDPOINT_HOST,
                                                                        port=OPEN_TELEMETRY_ENDPOINT_PORT))))
# provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

# Sets the global default tracer provider
trace.set_tracer_provider(provider)
#
# # Creates a tracer from the global tracer provider
tracer = trace.get_tracer(__name__)


FlaskInstrumentor().instrument_app(app)


@app.route("/hello")
def delayed_hello():
    # with tracer.start_as_current_span("/hello") as parent:
    start = datetime.now()
    span = trace.get_current_span()

    randsleep = random.uniform(0, 4)
    sleep(randsleep)

    for i in range(4):
        with tracer.start_as_current_span("/hi") as child:
            requests.get("http://127.0.0.1:5000/hi")

    mylogger.log(logging.INFO, "http request",
                 extra={"app": "delayed-response-flask", "traceID": format(span.context.trace_id, 'x'),
                        "latency": (datetime.now() - start).total_seconds(), "path": "/hello"})

    return "Hello World! - Slept {} seconds".format(randsleep)

@app.route("/hi")
def delayed_hi():
    # start = datetime.now()
    # span = trace.get_current_span()

    randsleep = random.uniform(0, 4)
    sleep(randsleep)

    # mylogger.log(logging.INFO, "http request",
    #              extra={"app": "delayed-response-flask", "traceID": format(span.context.trace_id, 'x'),
    #                     "latency": (datetime.now() - start).total_seconds(), "path": "/hi"})
    return "Hi"


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":  # on running python app.py
    app.run(debug=True)  # run the flask app
