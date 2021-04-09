import json
import os
from distutils.util import strtobool

import requests
from flask import Flask, request
from py_zipkin.encoding import Encoding
from py_zipkin.request_helpers import create_http_headers
from py_zipkin.zipkin import zipkin_client_span, zipkin_span
from urllib.parse import urlencode

app = Flask(__name__)

SERVICE_NAME = os.environ.get("SERVICE_NAME")
INTENTIONAL_FAILURE_PCT = float(os.environ.get("INTENTIONAL_FAILURE_PCT", 0))
ZIPKIN_DSN = os.environ.get("ZIPKIN_DSN", "http://zipkin:9411/api/v2/spans")
ZIPKIN_SAMPLE_RATE = float(os.environ.get("ZIPKIN_SAMPLE_RATE", 100.0))
SERVICE2_URL = os.environ.get("SERVICE2_URL", "http://service2:5000/")
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


@zipkin_client_span(service_name=SERVICE_NAME, span_name=f"call_service2_from_{SERVICE_NAME}")
def call_service2(query_params):
    query_str = urlencode(query_params)
    return requests.get(f'{SERVICE2_URL}?{query_str}', headers=create_http_headers())


@zipkin_client_span(service_name=SERVICE_NAME, span_name=f"call_service3_from_{SERVICE_NAME}")
def call_service3(query_params):
    query_str = urlencode(query_params)
    return requests.get(f'{SERVICE3_URL}?{query_str}', headers=create_http_headers())


@app.route('/')
def index():
    with zipkin_span(
        service_name=SERVICE_NAME,
        span_name=f"{SERVICE_NAME}",
        transport_handler=default_handler,
        port=FLASK_PORT,
        sample_rate=ZIPKIN_SAMPLE_RATE,
        encoding=Encoding.V2_JSON,
        binary_annotations={"developer_info": {"name": "Deepak", "email": "deepak.nair@dataweave.com", "manager": "Ram"}}  # TODO(Deepak): Fetch this from git
    ) as zipkin_context:
        zipkin_context.update_binary_annotations({"user_headers": request.headers})

        # Query params to control failure rate and latency by  emulating a O(2^n) recursive implementation of
        # fibonacci algorithm.

        should_fail = request.args.get('fail')
        fibonacci = request.args.get('fibonacci')

        query_params = {
            'fail': should_fail.lower() if should_fail else 'false',
            'fibonacci':  fibonacci if fibonacci else "0"
        }
        # Simulating synchronous calls to different microservices
        service2_response = call_service2(query_params)
        service3_response = call_service3(query_params)

        return json.dumps({
            "should_fail": should_fail,
            "input": fibonacci,
            "response_codes": {
                "service2": service2_response.status_code,
                "service3": service3_response.status_code
            },
            "service3_response": service3_response.json()
        }, indent=4), 200


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT, threaded=False)
