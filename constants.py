PROMETHEUS_ENDPOINT = 'http://prometheus:9090'
ZIPKIN_API_ENDPOINT = f'http://zipkin:9411/api/v2'
LOOKBACK_PERIOD_MILLISECONDS = 1000 * 60
traces_api_request = f'{ZIPKIN_API_ENDPOINT}/traces?serviceName=service1&lookback={LOOKBACK_PERIOD_MILLISECONDS}'