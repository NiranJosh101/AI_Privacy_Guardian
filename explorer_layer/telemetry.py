import os  # Make sure to import os at the top
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def init_telemetry(app, service_name):
    resource = Resource.create(attributes={"service.name": service_name})
    provider = TracerProvider(resource=resource)
    
    # Check the environment variable before setting up the exporter
    if os.getenv("OTEL_TRACES_EXPORTER") != "none":
        exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
    

    
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)