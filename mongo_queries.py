from datetime import datetime, timedelta
from mongoengine import connect
from models import *
from constants import MONGO_HOST, MONGO_DB, MONGO_USERNAME
from collections import defaultdict



# Mongo Queries to be used by the chat bot
connect(db=MONGO_DB, username=MONGO_USERNAME, host=MONGO_HOST)


# Services that are failing.
failing_services_qs = SpanLatency.objects(response_status=FAILURE, span_kind=SERVER_KIND).distinct('span_name')
failing_services = [service_name for service_name in failing_services_qs]
print(f'Failing services are {", ".join(failing_services)}')

# Show top three traces of failing services
top_three_failing_traces_qry = [
    {"$match": {'span_kind': 'SERVER', 'response_status': 'FAILURE'}},
    {'$sort': {"duration": -1}},
    {"$group": {"_id": "$span_name", "trace_ids": {"$push": {"trace_id": "$trace_id"}}}},
    {"$project": {"trace_ids": {"$slice": ["$trace_ids", 3]}}}
]
top_three_failing_traces = SpanLatency.objects.aggregate(top_three_failing_traces_qry)
for result in top_three_failing_traces:
    service = result['_id']
    trace_ids = result['trace_ids']

    print(f'Service: {service}\nTrace Ids:\n')
    for trace_id in trace_ids:
        print(trace_id)
print()

# Services that are slower than x milliseconds
x = 220  # 220 ms
slow_services = SpanLatency.objects.aggregate([
    {"$match": {'span_kind': 'SERVER', 'response_status': 'SUCCESS'}},
    {"$group": {"_id": "$span_name", "average_latency": {"$avg": "$duration"}}},
    {"$match": {'average_latency': {'$gt': x * 1000}}},  # Milliseconds to Zipkin's microsecond conversion
])
print(f'Services having an average latency greater than {x} milliseconds.')

for result in slow_services:
    service = result['_id']
    average_latency = result['average_latency']
    print(f'{service} has an avg latency of {average_latency}')

print()

# Traces with the worst latency
traces_with_worst_latency = SpanLatency.objects.aggregate([
    {"$match": {'span_kind': 'SERVER', 'response_status': 'SUCCESS'}},
    {"$group": {"_id": "$trace_id", "latency": {"$sum": "$duration"}}},
    {"$sort": {'latency': -1}},
    {"$limit": 3}
])

print(f'Top three traces with worst latency')
for result in traces_with_worst_latency:
    trace_id = result['_id']
    latency = result['latency']
    print(f'Trace {trace_id} had a latency of {latency}')

print()

# Services which are degrading in performance

distinct_services = SpanLatency.objects(span_kind=SERVER_KIND).distinct('span_name')
for service in distinct_services:
    most_recent_span = SpanLatency.objects(span_name=service, span_kind=SERVER_KIND).order_by('-start_timestamp').first()
    most_recent_span_id = most_recent_span.id
    most_recent_span_duration = most_recent_span.duration
    avg_latency = SpanLatency.objects(span_name=service, span_id__ne=most_recent_span_id, span_kind=SERVER_KIND).average('duration')

    if most_recent_span_duration > avg_latency:
        print(f'''{service} is degrading in performance.\nDuration of latest request took {most_recent_span_duration} microseconds as opposed to an average latency of {avg_latency} microseconds''')

print()

# What is the load on service x ?
x = 'service1'
current_time = datetime.now()
previous_hour = current_time - timedelta(hours=1)
previous_hour_ts = previous_hour.timestamp()

avg_cpu_load = CpuLoad.objects(service_name=x).average('cpu_load')
hourly_avg_cpu_load = CpuLoad.objects(service_name=x, timestamp__gte=previous_hour_ts).average('cpu_load')

print(f'Avg CPU load for service {x} is {round(avg_cpu_load, 2)}% and the  hourly average is {round(hourly_avg_cpu_load, 2)}%')

avg_mem_usage = MemLoad.objects(service_name=x).average('mem_load_bytes')
hourly_avg_mem_usage = MemLoad.objects(service_name=x, timestamp__gte=previous_hour_ts).average('mem_load_bytes')

print(f'Avg memory consumption for service {x} is {int(avg_mem_usage)} bytes and the hourly average is {int(hourly_avg_mem_usage)} bytes')

print()


# Who is the developer of service x?
x = 'service1'
latest_service_span = SpanLatency.objects(span_name=x, span_kind=SERVER_KIND).order_by('-start_timestamp').first()
developer_details = latest_service_span.developer_details
print(f'Developer details for service {x}.')
for k, v in developer_details.items():
    print(f'{k}: {v}')

print()

# Other details of service x?
latest_service_span = SpanLatency.objects(span_name=x, span_kind=SERVER_KIND).order_by('-start_timestamp').first()
metadata = latest_service_span.metadata
print(f'Other details for service {x}.')
for k, v in metadata.items():
    print(f'{k}: {v}')

print()

# Dependent services due to service x
x = 'service3'
latest_service_span = SpanLatency.objects(span_name=x, span_kind=SERVER_KIND).order_by('-duration').first()
trace_id_of_latest_service_span = latest_service_span.trace_id
spans = SpanLatency.objects(trace_id=trace_id_of_latest_service_span, span_kind=SERVER_KIND)

service_name_span_id_map = {}
service_dependency_map = defaultdict(list)

for span in spans:
    service_name_span_id_map[span.span_id] = span

for span in spans:
    span_id = span.span_id
    span_name = span.span_name
    parent_id = span.parent_id

    dependency_list = service_dependency_map[span_name]
    parent_span_obj = service_name_span_id_map.get(parent_id)
    if parent_span_obj:
        dependency_list.append(parent_span_obj)


print(f'Operations affected due to {x} for the slowest trace are:')
affected_spans = service_dependency_map.get(x, [])
for span in affected_spans:
    print(f'{span.span_name}\t Latency: {span.duration // 1000} milliseconds')
