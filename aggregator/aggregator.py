from prometheus_api_client import PrometheusConnect, MetricsList, Metric
prometheus_client = PrometheusConnect(url='http://prometheus:9090', disable_ssl=True)

# CPU Usage Query
cpu_metric_data = prometheus_client.custom_query(
    query='sum by (name) (rate(container_cpu_usage_seconds_total{image!="",container_label_org_label_schema_group=""}[1m])) / scalar(count(node_cpu_seconds_total{mode="user"})) * 100'
)

# Memory Usage Query
mem_metric_data = prometheus_client.custom_query(
    query='sum by (name)(container_memory_usage_bytes{image!="",container_label_org_label_schema_group=""})'
)


def parse_prom_metrics(metric_dict):
    metric_name = metric_dict['metric']['name']
    ts, metric_value = metric_dict['value']
    print(f'{metric_name} -> {metric_value}')
    return metric_name, metric_value


for metric_dict in cpu_metric_data:
    parse_prom_metrics(metric_dict)

for metric_dict in mem_metric_data:
    parse_prom_metrics(metric_dict)


