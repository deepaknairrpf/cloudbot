from mongoengine import Document, StringField, LongField, DictField, FloatField

SUCCESS = 'success'
FAILURE = 'failure'
ROOT = 'root'

STATUS_CHOICES = (
    (SUCCESS, 'success'),
    (FAILURE, 'failure')
)

SERVER_KIND = 'SERVER'
CLIENT_KIND = 'CLIENT'

SPAN_KIND = (
    (SERVER_KIND, 'SERVER'),
    (CLIENT_KIND, 'CLIENT')
)


class SpanLatency(Document):
    meta = {
        'indexes': ['span_name', 'duration']
    }
    span_name = StringField(max_length=1000, required=True)
    span_kind = StringField(max_length=20, choices=SPAN_KIND)
    start_timestamp = LongField()
    duration = LongField()
    tags = DictField()
    status = StringField(choices=STATUS_CHOICES)
    trace_id = StringField(max_length=32, min_length=16, required=True)
    parent_id = StringField(max_length=16, min_length=16, default=ROOT)
    span_id = StringField(max_length=16, min_length=16, required=True, unique_with=['trace_id', 'span_kind'])


class CpuLoad(Document):
    service_name = StringField(required=True)
    timestamp = LongField(required=True)
    cpu_load = FloatField(required=True)


class MemLoad(Document):
    service_name = StringField(required=True)
    timestamp = LongField(required=True)
    mem_load_bytes = LongField(required=True)
