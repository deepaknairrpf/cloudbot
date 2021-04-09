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
    {"$project": {"trace_ids": {"$slice":["$trace_ids", 2]}}}
]
top_three_failing_traces = SpanLatency.objects.aggregate(top_three_failing_traces_qry)
for result in top_three_failing_traces:
    service = result['_id']
    trace_ids = result['trace_ids']

    print(f'Service: {service}\nTrace Ids:\n')
    for trace_id in trace_ids:
        print(trace_id)