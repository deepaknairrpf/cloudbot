from mongoengine import connect
from models import *
from constants import MONGO_HOST, MONGO_DB, MONGO_USERNAME




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
print(f'Services having an average latency lesser than {x} milliseconds.')

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
