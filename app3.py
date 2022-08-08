# app.py
import os
import random
from time import sleep

from flask import Flask  # import flask
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

# from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)  # create an app instance

trace.set_tracer_provider(TracerProvider())

trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

trace.get_tracer_provider().add_span_processor(
   BatchSpanProcessor(OTLPSpanExporter(endpoint="otlp-grpc-tempo.tools.memed.rocks:4317"))
)

FlaskInstrumentor().instrument_app(app)


@app.route("/hello")
def hello():
    randsleep = random.uniform(0, 4)
    sleep(randsleep)
    return "Hello World! - Slept {} seconds".format(randsleep)


if __name__ == "__main__":  # on running python app.py
    app.run()  # run the flask app