import os
import time
from distutils.util import strtobool
import traceback
import requests
from flask import Flask, request
from py_zipkin.encoding import Encoding
from py_zipkin.zipkin import ZipkinAttrs, zipkin_client_span, zipkin_span

app = Flask(__name__)

SERVICE_NAME = os.environ.get("SERVICE_NAME")
ZIPKIN_DSN = os.environ.get("ZIPKIN_DSN", "http://zipkin:9411/api/v2/spans")
ZIPKIN_SAMPLE_RATE = float(os.environ.get("ZIPKIN_SAMPLE_RATE", 100.0))
FLASK_DEBUG = strtobool(os.environ.get("FLASK_DEBUG", "false").lower())
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))


def default_handler(encoded_span):
    body = encoded_span
    app.logger.debug("body %s", body)

    return requests.post(
        ZIPKIN_DSN,
        data=body,
        headers={"Content-Type": "application/json"},
    )


@app.before_request
def log_request_info():
    app.logger.debug("Headers: %s", request.headers)
    app.logger.debug("Body: %s", request.get_data())


@zipkin_client_span(service_name=SERVICE_NAME, span_name=f'compute_factorial_{SERVICE_NAME}')
def compute_factorial(query_params):

    def factorial(input: int):
        """An O(2^n) implementation of factorial function to simulate an API with bad latency and stack
        memory consumption"""

        # Base Case
        if input == 0:
            return 1

        return input * factorial(input - 1)

    factorial_query_param = query_params.get('factorial')
    num = 0
    try:
        num = int(factorial_query_param)

    except ValueError as ve:
        print(ve)
        traceback.print_exc()

    result = factorial(num)
    return {'factorial_result': result, 'num': num}


@app.route("/")
def index():
    with zipkin_span(
        service_name=SERVICE_NAME,
        zipkin_attrs=ZipkinAttrs(
            trace_id=request.headers["X-B3-TraceID"],
            span_id=request.headers["X-B3-SpanID"],
            parent_span_id=request.headers["X-B3-ParentSpanID"],
            flags=request.headers['X-B3-Flags'],
            is_sampled=request.headers["X-B3-Sampled"],
        ),
        span_name=f"{SERVICE_NAME}",
        transport_handler=default_handler,
        port=FLASK_PORT,
        sample_rate=ZIPKIN_SAMPLE_RATE,
        encoding=Encoding.V2_JSON,
        binary_annotations={'dev': 'Deepak'}
    ):
        factorial = request.args.get('factorial')

        query_params = {
            'factorial': factorial if factorial else "0"
        }

        return compute_factorial(query_params), 200


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT, threaded=False)

