from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import tempfile
import time
from collections import defaultdict, deque
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse, Response

from .algorithms import fibonacci, gcd
from .doc_qa import QADocument, QAService
from .excel_tools import write_rows_to_excel
from .logging_utils import setup_json_logging
from .ml_pipeline import TrainedModel, train_linear_regression
from .ml_pipeline import predict as ml_predict
from .monitor import PING_HISTOGRAM, PingResult, ping_url
from .system_metrics import metrics_broadcaster
from .websocket_manager import ConnectionManager

setup_json_logging()
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup/shutdown tasks."""
    asyncio.create_task(metrics_broadcaster(_ws_manager, interval=2.0))
    logger.info("metrics_broadcaster_started")
    yield


app = FastAPI(title="Python Mastery API", description="Examples: Fibonacci, VIN, ML, RAG.", lifespan=lifespan)

_qa = QAService()

# WebSocket connection manager for real-time monitoring
_ws_manager = ConnectionManager()

# Default ML model for /ml/predict; trained at startup on a simple pattern
_ml_model: TrainedModel | None = None


def _init_default_ml_model() -> None:
    global _ml_model
    try:
        x = [[1.0, 2.0], [2.0, 3.0], [3.0, 4.0], [4.0, 5.0]]
        y = [3.0, 5.0, 7.0, 9.0]
        _ml_model = train_linear_regression(x, y)
    except Exception:  # pragma: no cover
        logger.exception("failed_default_model")
        _ml_model = None


_init_default_ml_model()


_rate_buckets: dict[str, deque[float]] = defaultdict(deque)
_RATE_LIMIT_MAX = 120
_RATE_LIMIT_WINDOW = 60.0


def _check_rate_limit(req: Request, max_req: int = _RATE_LIMIT_MAX) -> None:
    now = monotonic()
    ip = (req.client.host if req.client else "unknown") or "unknown"
    dq = _rate_buckets[ip]
    while dq and now - dq[0] > _RATE_LIMIT_WINDOW:
        dq.popleft()
    if len(dq) >= max_req:
        from fastapi import HTTPException

        raise HTTPException(status_code=429, detail="rate limit exceeded")
    dq.append(now)


@dataclass
class FibResponse:
    n: int
    value: int


@dataclass
class GcdResponse:
    a: int
    b: int
    gcd: int


@app.get(
    "/fib/{n}",
    response_model=FibResponse,
    tags=["examples"],
    summary="Compute the n-th Fibonacci number",
    responses={
        200: {
            "description": "Fibonacci result",
            "content": {"application/json": {"example": {"n": 10, "value": 55}}},
        }
    },
)
def fib_endpoint(n: int) -> FibResponse:
    if n < 0:
        n = 0
    value = fibonacci(n)
    logger.info("fib", extra={"n": n, "value": value})
    return FibResponse(n=n, value=value)


@app.get(
    "/math/gcd",
    response_model=GcdResponse,
    tags=["examples"],
    summary="Compute the greatest common divisor of two integers",
)
def gcd_endpoint(a: int, b: int) -> GcdResponse:
    from fastapi import HTTPException

    try:
        value = gcd(a, b)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    logger.info("gcd", extra={"a": a, "b": b, "gcd": value})
    return GcdResponse(a=a, b=b, gcd=value)


class VinRequest(BaseModel):
    vin: str = Field(..., min_length=11, max_length=64)
    model_config = {"json_schema_extra": {"examples": [{"vin": "1HGCM82633A004352"}]}}


class VinResponse(BaseModel):
    vin: str
    valid: bool
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"vin": "1HGCM82633A004352", "valid": True},
                {"vin": "INVALIDVIN1234567", "valid": False},
            ]
        }
    }


@app.post(
    "/vin/validate",
    response_model=VinResponse,
    tags=["examples"],
    summary="Validate a VIN using ISO 3779 (check digit)",
)
def vin_validate_api(req: VinRequest, request: Request) -> VinResponse:
    from .vin import is_valid_vin

    _check_rate_limit(request)
    valid = bool(is_valid_vin(req.vin))
    logger.info("vin_validate", extra={"vin_len": len(req.vin), "valid": valid})
    return VinResponse(vin=req.vin, valid=valid)


class VinDecodedResponse(BaseModel):
    vin: str
    valid: bool
    wmi: str
    vds: str
    vis: str
    check_digit: str
    check_digit_valid: bool | None
    model_year_code: str | None
    model_year: int | None
    model_year_candidates: list[int] | None
    plant_code: str | None
    serial_number: str | None
    region: str | None
    brand: str | None
    notes: list[str] | None


@app.post(
    "/vin/decode",
    response_model=VinDecodedResponse,
    tags=["examples"],
    summary="Decode structural VIN fields (WMI/VDS/VIS, year, plant, etc)",
)
def vin_decode_api(req: VinRequest, request: Request) -> Response:
    from .vin import decode_vin

    dec = decode_vin(req.vin)
    logger.info("vin_decode", extra={"valid": dec.valid, "wmi": dec.wmi})
    _check_rate_limit(request)
    payload = VinDecodedResponse(**dec.__dict__).model_dump()
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    etag = hashlib.md5(raw).hexdigest()  # noqa: S324 demo-only weak hash ok
    inm = request.headers.get("If-None-Match")
    headers = {
        "ETag": etag,
        "Cache-Control": "public, max-age=3600",
    }
    if inm == etag:
        return Response(status_code=304, headers=headers)
    return JSONResponse(content=payload, headers=headers)


class VinGenerateRequest(BaseModel):
    wmi: str = Field(..., min_length=3, max_length=3, examples=["1HG"])
    vds: str = Field(..., min_length=5, max_length=5, examples=["CM826"])
    year: int = Field(..., ge=1980, le=2039, examples=[2003])
    plant_code: str = Field(..., min_length=1, max_length=1, examples=["A"])
    serial: str = Field(..., min_length=6, max_length=6, examples=["004352"])


class VinGenerateResponse(BaseModel):
    vin: str


@app.post(
    "/vin/generate",
    response_model=VinGenerateResponse,
    tags=["examples"],
    summary="Generate a valid VIN (computes check digit)",
)
def vin_generate_api(req: VinGenerateRequest, request: Request) -> VinGenerateResponse:
    from .vin import generate_vin

    _check_rate_limit(request)
    try:
        vin = generate_vin(req.wmi, req.vds, req.year, req.plant_code, req.serial)
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e)) from e
    logger.info("vin_generate", extra={"wmi": req.wmi, "year": req.year})
    return VinGenerateResponse(vin=vin)


@app.middleware("http")
async def add_timing_header(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    start = time.perf_counter()
    req_id = request.headers.get("X-Request-ID") or uuid4().hex
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}ms"
    response.headers["X-Request-ID"] = req_id
    logger.info("request", extra={"path": request.url.path, "method": request.method, "status_code": response.status_code, "ms": round(elapsed_ms, 2), "request_id": req_id})
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/monitor/ping")
def monitor_ping(url: str) -> PingResult:
    return ping_url(url)


@app.get("/metrics")
def metrics() -> Response:
    # Lazy import to avoid hard dependency if not installed
    prometheus: Any | None = None
    try:
        import prometheus_client as prometheus  # runtime optional
    except Exception:  # pragma: no cover - import may fail when not installed
        prometheus = None
        content_type_latest = "text/plain; version=0.0.4; charset=utf-8"
    else:
        # prometheus is a module at this point
        content_type_latest = getattr(
            prometheus,
            "CONTENT_TYPE_LATEST",
            "text/plain; version=0.0.4; charset=utf-8",
        )

    if PING_HISTOGRAM is None or prometheus is None:
        # Expose an empty payload to avoid 500s when optional dep is missing
        return Response(content=b"", media_type=content_type_latest)
    data = prometheus.generate_latest()
    return Response(content=data, media_type=content_type_latest)


# --- Document Q&A ---


@app.post("/qa/documents")
def qa_add_documents(docs: list[str]) -> dict[str, list[int]]:
    ids = _qa.add(docs)
    return {"ids": ids}


class QADocumentIn(BaseModel):
    id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class QAIngestRequest(BaseModel):
    documents: list[QADocumentIn]
    chunk_size: int = Field(default=800, ge=100, le=10_000)
    chunk_overlap: int = Field(default=100, ge=0, le=5_000)
    reset: bool = Field(default=False)


class QAIngestResponse(BaseModel):
    status: str
    ids: list[int]
    n_chunks: int


@app.post(
    "/qa/ingest",
    response_model=QAIngestResponse,
    tags=["rag"],
    summary="Ingest structured documents (chunked) for offline RAG",
)
def qa_ingest(req: QAIngestRequest) -> QAIngestResponse:
    if req.reset:
        _qa.reset()
    docs = [
        QADocument(id=d.id, text=d.text, metadata={str(k): v for k, v in d.metadata.items()})
        for d in req.documents
    ]
    ids = _qa.add_documents(docs, chunk_size=req.chunk_size, chunk_overlap=req.chunk_overlap)
    return QAIngestResponse(status="ok", ids=ids, n_chunks=len(ids))


@app.post("/qa/search")
def qa_search(query: str, k: int = 5) -> dict[str, object]:
    hits = _qa.search(query, k=k)
    return {"hits": hits}


@app.post("/qa/search_rich")
def qa_search_rich(query: str, k: int = 5) -> dict[str, object]:
    hits = _qa.search_rich(query, k=k)
    payload = [{"id": h.id, "score": h.score, "text": h.text, "meta": h.meta} for h in hits]
    return {"hits": payload}


@app.post("/qa/ask")
def qa_ask(question: str, k: int = 3) -> dict[str, object]:
    return _qa.ask(question, k=k)


@app.post("/qa/ask_rich")
def qa_ask_rich(question: str, k: int = 3) -> dict[str, object]:
    return _qa.ask_rich(question, k=k)


@app.post("/qa/reset")
def qa_reset() -> dict[str, str]:
    _qa.reset()
    return {"status": "reset"}


@app.post("/qa/config")
def qa_config(embedder: str, index: str) -> dict[str, str]:
    try:
        _qa.configure(embedder, index)
    except Exception as e:  # noqa: BLE001 - return as bad request
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"status": "ok", "embedder": embedder, "index": index}


# --- Excel Export ---


class ExcelExportRequest(BaseModel):
    rows: list[list[str]]


@app.post(
    "/excel/export",
    tags=["examples"],
    summary="Generate an Excel file from rows of strings",
    responses={
        200: {
            "description": "XLSX file attachment",
            "content": {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {}},
        }
    },
)
def excel_export_api(req: ExcelExportRequest) -> Response:
    """Return an .xlsx file generated from the provided rows.

    Uses the existing utility `write_rows_to_excel`. A temporary file is created
    and returned as an attachment.
    """
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "export.xlsx"
        write_rows_to_excel(req.rows, path)
        data = path.read_bytes()
    headers = {"Content-Disposition": 'attachment; filename="export.xlsx"'}
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


# --- ML Endpoints ---


class MLPredictRequest(BaseModel):
    rows: list[list[float]]


class MLPredictResponse(BaseModel):
    predictions: list[float]


@app.post(
    "/ml/predict",
    tags=["ml"],
    response_model=MLPredictResponse,
    summary="Predict using a default linear regression model",
)
def ml_predict_api(req: MLPredictRequest) -> MLPredictResponse:
    if _ml_model is None:
        # Initialize lazily if needed
        _init_default_ml_model()
        if _ml_model is None:
            from fastapi import HTTPException

            raise HTTPException(status_code=500, detail="model not available")
    preds = ml_predict(_ml_model, req.rows)
    return MLPredictResponse(predictions=preds)


class MLTrainRequest(BaseModel):
    x: list[list[float]]
    y: list[float]
    set_default: bool = Field(
        default=True,
        description="If true, update the service's default model",
    )


class MLTrainResponse(BaseModel):
    status: str
    n_rows: int


@app.post(
    "/ml/train",
    tags=["ml"],
    response_model=MLTrainResponse,
    summary="Train a linear regression model (optionally set as default)",
)
def ml_train_api(req: MLTrainRequest) -> MLTrainResponse:
    global _ml_model
    if len(req.x) != len(req.y):
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="x and y lengths differ")
    model = train_linear_regression(req.x, req.y)
    if req.set_default:
        _ml_model = model
    return MLTrainResponse(status="ok", n_rows=len(req.x))


# --- WebSocket Real-time Monitoring ---


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time system metrics."""
    await _ws_manager.connect(websocket)
    try:
        # Keep connection alive and handle any incoming messages
        while True:
            # We don't expect client messages for metrics, but need to listen
            # to detect disconnections
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            except asyncio.TimeoutError:
                # No message received, continue
                continue
    except WebSocketDisconnect:
        _ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning("websocket_error", extra={"error": str(e)})
        _ws_manager.disconnect(websocket)


@app.get("/monitor/connections")
def get_websocket_connections() -> dict[str, int]:
    """Get current WebSocket connection count."""
    return {"active_connections": _ws_manager.get_connection_count()}
