from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

def init_telemetry(app, service_name):
    # 1. Setup the Tracer with the specific service name
    resource = Resource.create(attributes={"service.name": service_name})
    provider = TracerProvider(resource=resource)
    
    # 2. Setup the Exporter to send data to Jaeger
    # Tip: In production, change 'jaeger' to an environment variable
    exporter = OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    # 3. Instrument the FastAPI app
    FastAPIInstrumentor.instrument_app(app)