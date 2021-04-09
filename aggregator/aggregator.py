import traceback
import json
from json.decoder import JSONDecodeError

import requests
from mongoengine import connect
from mongoengine.errors import NotUniqueError, ValidationError
from prometheus_api_client import PrometheusConnect

from constants import PROMETHEUS_ENDPOINT, MONGO_DB, MONGO_USERNAME, MONGO_HOST
from constants import traces_api_request
from models import *

connect(db=MONGO_DB, username=MONGO_USERNAME, host=MONGO_HOST)
prometheus_client = PrometheusConnect(url=PROMETHEUS_ENDPOINT, disable_ssl=True)

# CPU Usage Query
cpu_metric_data = prometheus_client.custom_query(
    query='sum by (name) (rate(container_cpu_usage_seconds_total{image!="",container_label_org_label_schema_group=""}[1m])) / scalar(count(node_cpu_seconds_total{mode="user"})) * 100'
)

# Memory Usage Query
mem_metric_data = prometheus_client.custom_query(
    query='sum by (name)(container_memory_usage_bytes{image!="",container_label_org_label_schema_group=""})'
)


def parse_prom_metrics(metric_dict, type='cpu'):
    metric_name = metric_dict['metric']['name']
    ts, metric_value = metric_dict['value']
    print(f'{metric_name} -> {metric_value}')

    if type == 'cpu':
        cpu_load = CpuLoad(service_name=metric_name, timestamp=ts, cpu_load=metric_value)
        cpu_load.save()

    elif type == 'mem':
        mem_load = MemLoad(service_name=metric_name, timestamp=ts, mem_load_bytes=metric_value)
        mem_load.save()

    else:
        raise ValueError(f'type needs to be either cpu or mem.')

    return metric_name, metric_value


for metric_dict in cpu_metric_data:
    parse_prom_metrics(metric_dict, type='cpu')

for metric_dict in mem_metric_data:
    parse_prom_metrics(metric_dict, type='mem')


spans = []

try:
    traces_response = requests.get(traces_api_request)

    for trace_list in traces_response.json():
        try:
            for trace_info in trace_list:
                span_name = trace_info['name']
                span_id = trace_info['id']
                parent_id = trace_info.get('parentId', ROOT)
                trace_id = trace_info['traceId']
                duration = trace_info['duration']
                start_timestamp = trace_info['timestamp']
                span_kind = trace_info['kind']

                tags = trace_info.get('tags', {})
                service_endpoint_metadata = trace_info.get('localEndpoint', {})

                metadata = dict(tags, **service_endpoint_metadata)
                developer_details = metadata.get('developer_info', "")
                developer_details = json.loads(developer_details.replace('\'', '\"')) if developer_details else {}
                metadata['developer_info'] = developer_details

                status = SUCCESS if "error" not in metadata else FAILURE

                span_latency = SpanLatency(
                    span_name=span_name,
                    span_kind=span_kind,
                    start_timestamp=start_timestamp,
                    duration=duration,
                    metadata=metadata,
                    response_status=status,
                    trace_id=trace_id,
                    parent_id=parent_id,
                    span_id=span_id,
                    developer_details=developer_details,
                )
                print(f'Saving distributed trace stats for {span_latency.span_name} service.')
                span_latency.save()

        except JSONDecodeError as jde:
            print(jde)
            traceback.print_exc()
            print(f'API did not return a valid JSON')

        except KeyError as ke:
            print(ke)
            traceback.print_exc()
            print(f'API response did not have mandatory keys')

        except NotUniqueError as nue:
            print(f'Skipping record as it already exists')

        except ValidationError as ve:
            print(ve)
            traceback.print_exc()

except Exception as exc:
    print(exc)
    traceback.print_exc()
    print(f'Failed to parse API response')


