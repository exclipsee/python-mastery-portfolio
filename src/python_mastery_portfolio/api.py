from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from starlette.responses import Response

from .algorithms import fibonacci
from .doc_qa import QAService
from .logging_utils import setup_json_logging
from .monitor import PING_HISTOGRAM, PingResult, ping_url

setup_json_logging()
logger = logging.getLogger("api")
app = FastAPI(
    title="Python Mastery API",
    description=(
        "Typed FastAPI service with examples: Fibonacci, VIN validation. "
        "Includes timing middleware, request-id propagation, and JSON logging."
    ),
)

_qa = QAService()


@dataclass
class FibResponse:
    n: int
    value: int


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
def vin_validate_api(req: VinRequest) -> VinResponse:
    from .vin import is_valid_vin

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
def vin_decode_api(req: VinRequest) -> VinDecodedResponse:
    from .vin import decode_vin

    dec = decode_vin(req.vin)
    logger.info("vin_decode", extra={"valid": dec.valid, "wmi": dec.wmi})
    return VinDecodedResponse(**dec.__dict__)


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
def vin_generate_api(req: VinGenerateRequest) -> VinGenerateResponse:
    from .vin import generate_vin

    try:
        vin = generate_vin(req.wmi, req.vds, req.year, req.plant_code, req.serial)
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e)) from e
    logger.info("vin_generate", extra={"wmi": req.wmi, "year": req.year})
    return VinGenerateResponse(vin=vin)


@app.middleware("http")
async def add_timing_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start = time.perf_counter()
    # Propagate or assign a request ID
    req_id = request.headers.get("X-Request-ID") or uuid4().hex
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}ms"
    response.headers["X-Request-ID"] = req_id
    logger.info(
        "request",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "ms": round(elapsed_ms, 2),
            "request_id": req_id,
        },
    )
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
    pc: Any | None
    try:
        import prometheus_client as pc  # runtime optional
    except Exception:  # pragma: no cover - import may fail when not installed
        pc = None
        content_type_latest = "text/plain; version=0.0.4; charset=utf-8"
    else:
        # pc is a module at this point
        content_type_latest = getattr(
            pc,
            "CONTENT_TYPE_LATEST",
            "text/plain; version=0.0.4; charset=utf-8",
        )

    if PING_HISTOGRAM is None or pc is None:
        # Expose an empty payload to avoid 500s when optional dep is missing
        return Response(content=b"", media_type=content_type_latest)
    data = pc.generate_latest()
    return Response(content=data, media_type=content_type_latest)


# --- Document Q&A ---

@app.post("/qa/documents")
def qa_add_documents(docs: list[str]) -> dict[str, list[int]]:
    ids = _qa.add(docs)
    return {"ids": ids}


@app.post("/qa/search")
def qa_search(query: str, k: int = 5) -> dict[str, object]:
    hits = _qa.search(query, k=k)
    return {"hits": hits}


@app.post("/qa/ask")
def qa_ask(question: str, k: int = 3) -> dict[str, object]:
    return _qa.ask(question, k=k)


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
