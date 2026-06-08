import functools
import os
from pathlib import Path
from typing import Any, Callable, TypeVar

# Manual OpenTelemetry Imports
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

F = TypeVar("F", bound=Callable[..., Any])
_tracer = None
_provider = None

def _load_env_file() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

def _debug(message: str) -> None:
    try:
        Path("outputs").mkdir(exist_ok=True)
        with Path("outputs/phoenix_debug.log").open("a", encoding="utf-8") as file:
            file.write(message + "\n")
    except Exception:
        pass

def configure_tracing() -> None:
    global _tracer, _provider
    if _tracer is not None:
        return

    _load_env_file()
    try:
        # Import the Resource class to set the project name
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        import os

        # 1. Define the endpoint
        endpoint = "http://localhost:6006/v1/traces"
        
        # 2. Create a Resource. This is what tells Phoenix the PROJECT NAME.
        # 'service.name' is the magic key that Phoenix uses for the project name.
        resource = Resource.create({"service.name": "OmniTrip-Local"})
        
        # 3. Manually create the Exporter
        exporter = OTLPSpanExporter(endpoint=endpoint)
        
        # 4. Setup the Provider WITH the resource
        provider = TracerProvider(resource=resource) # <--- Added resource here
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
        
        # 5. Set as the global provider
        trace.set_tracer_provider(provider)
        
        _provider = provider
        _tracer = trace.get_tracer("matchdayops")
        
        _debug(f"MANUAL Tracing configured. Project: OmniTrip-Local, Endpoint: {endpoint}")

        try:
            from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor
            GoogleGenAIInstrumentor().instrument()
        except Exception:
            pass
            
    except Exception as exc:
        _debug(f"Manual tracing failed: {type(exc).__name__}: {exc}")
        _tracer = False

def flush_tracing() -> None:
    # The BatchSpanProcessor doesn't have a simple flush, 
    # but we can shut down the provider to force export.
    if _provider:
        try:
            _provider.shutdown()
        except Exception:
            pass

def traced(name: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            configure_tracing()
            if not _tracer:
                return func(*args, **kwargs)
            
            # Manual span management
            with _tracer.start_as_current_span(name) as span:
                span.set_attribute("matchdayops.function", func.__name__)
                result = func(*args, **kwargs)
                span.set_attribute("matchdayops.success", True)
                return result
        return wrapper
    return decorator
