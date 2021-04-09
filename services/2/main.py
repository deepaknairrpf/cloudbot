import os
from distutils.util import strtobool
import requests
from flask import Flask, request
from py_zipkin.encoding import Encoding
from py_zipkin.request_helpers import create_http_headers
from py_zipkin.zipkin import ZipkinAttrs, zipkin_client_span, zipkin_span
from urllib.parse import urlencode

app = Flask(__name__)

SERVICE_NAME = os.environ.get("SERVICE_NAME")
INTENTIONAL_FAILURE_PCT = float(os.environ.get("INTENTIONAL_FAILURE_PCT", 0))
ZIPKIN_DEBUG = strtobool(os.environ.get("ZIPKIN_DEBUG", "false").lower())
ZIPKIN_DSN = os.environ.get("ZIPKIN_DSN", "http://zipkin:9411/api/v2/spans")
ZIPKIN_SAMPLE_RATE = float(os.environ.get("ZIPKIN_SAMPLE_RATE", 100.0))
SERVICE3_URL = os.environ.get("SERVICE3_URL", "http://service3:5000/")
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


@zipkin_client_span(service_name=SERVICE_NAME, span_name=f"call_service3_from_{SERVICE_NAME}")
def call_service3(query_params):
    should_fail_query_param = query_params.get('fail')
    should_fail = True if should_fail_query_param == 'true' else False
    query_str = urlencode(query_params)

    # Intentional chance to fail
    if should_fail:
        raise Exception(f"Intentional failure")

    service3_response = requests.get(f'{SERVICE3_URL}?{query_str}', headers=create_http_headers())
    return service3_response.json()


@app.route("/")
def index():
    with zipkin_span(
        service_name=SERVICE_NAME,
        zipkin_attrs=ZipkinAttrs(
            trace_id=request.headers["X-B3-TraceID"],
            span_id=request.headers["X-B3-SpanID"],
            parent_span_id=request.headers["X-B3-ParentSpanID"],
            # Debug is encoded as X-B3-Flags: 1.
            flags=1 if ZIPKIN_DEBUG else 0,
            is_sampled=request.headers["X-B3-Sampled"],
        ),
        span_name=f"{SERVICE_NAME}",
        transport_handler=default_handler,
        port=FLASK_PORT,
        sample_rate=ZIPKIN_SAMPLE_RATE,
        encoding=Encoding.V2_JSON,
        binary_annotations={'dev': 'Deepak'}
    ):
        should_fail = request.args.get('fail')
        fibonacci = request.args.get('fibonacci')

        query_params = {
            'fail': should_fail.lower() if should_fail else 'false',
            'fibonacci':  fibonacci if fibonacci else "0"
        }

        return call_service3(query_params), 200


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT, threaded=False)

