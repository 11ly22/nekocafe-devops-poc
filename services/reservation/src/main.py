"""预约服务 FastAPI 入口"""
import os
import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ===== 日志配置（结构化 JSON）=====
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger()

# ===== OpenTelemetry 初始化（可选，容器内 pkg_resources 缺失时降级）=====
trace = None
try:
    from opentelemetry import trace as otel_trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    service_name = os.getenv("OTEL_SERVICE_NAME", "reservation")
    provider = TracerProvider()
    exporter = OTLPSpanExporter(endpoint=otel_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    otel_trace.set_tracer_provider(provider)
    trace = otel_trace
    _FastAPIInstrumentor = FastAPIInstrumentor
except Exception as exc:
    logger.warning("otel.init.skipped", error=str(exc))
    _FastAPIInstrumentor = None

# ===== FastAPI 应用 =====
app = FastAPI(
    title="NekoCafé Reservation Service",
    description="预约服务 - 负责在线预约、并发锁、容量管理",
    version="1.0.0",
)

if _FastAPIInstrumentor:
    _FastAPIInstrumentor.instrument_app(app)

VERSION = "1.0.0"
ENV = os.getenv("ENV", "dev")


# ===== 健康检查端点 =====
@app.get("/healthz")
async def healthz():
    """健康检查接口，供 K8s Liveness Probe 使用"""
    return {"status": "ok", "service": "reservation", "version": VERSION, "env": ENV}


# ===== 预约相关路由 =====
@app.post("/api/v1/reservations")
async def create_reservation(request: Request):
    """创建预约"""
    body = await request.json()
    span = trace.get_current_span() if trace else None
    trace_id = (
        format(span.get_span_context().trace_id, "032x")
        if span and span.is_recording()
        else "no-trace"
    )

    logger.info(
        "reservation.create",
        store_id=body.get("store_id"),
        date=body.get("date"),
        trace_id=trace_id,
    )

    # PoC 演示：直接返回模拟数据
    return JSONResponse(
        status_code=201,
        content={
            "reservation_id": f"rsv-{trace_id[:8]}",
            "store_id": body.get("store_id"),
            "date": body.get("date"),
            "time_slot": body.get("time_slot"),
            "cat_count": body.get("cat_count", 1),
            "status": "pending",
            "trace_id": trace_id,
        },
    )


@app.get("/api/v1/reservations/{reservation_id}")
async def get_reservation(reservation_id: str):
    """查询预约"""
    return {
        "reservation_id": reservation_id,
        "status": "confirmed",
        "store_id": "BJ-001",
        "date": "2026-05-15",
        "time_slot": "14:00",
        "cat_count": 2,
    }


@app.get("/api/v1/stores/{store_id}/availability")
async def get_availability(store_id: str, date: str = "2026-05-15"):
    """查询门店容量"""
    return {
        "store_id": store_id,
        "date": date,
        "slots": [
            {"time": "10:00", "capacity": 8, "booked": 3},
            {"time": "14:00", "capacity": 8, "booked": 7},
            {"time": "16:00", "capacity": 8, "booked": 0},
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
