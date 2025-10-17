from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from fastapi import FastAPI, Request
from starlette.responses import Response
from pydantic import BaseModel, Field

from .algorithms import fibonacci
from .logging_utils import setup_json_logging

setup_json_logging()
logger = logging.getLogger("api")
app = FastAPI(
    title="Python Mastery API",
    description=(
        "Typed FastAPI service with examples: Fibonacci, VIN validation. "
        "Includes timing middleware and JSON logging."
    ),
)


@dataclass
class FibResponse:
    n: int
    value: int


@app.get("/fib/{n}", response_model=FibResponse)
def fib_endpoint(n: int) -> FibResponse:
    if n < 0:
        n = 0
    value = fibonacci(n)
    logger.info("fib", extra={"n": n, "value": value})
    return FibResponse(n=n, value=value)


class VinRequest(BaseModel):
    vin: str = Field(..., min_length=11, max_length=64)


class VinResponse(BaseModel):
    vin: str
    valid: bool


@app.post("/vin/validate", response_model=VinResponse)
def vin_validate_api(req: VinRequest) -> VinResponse:
    from .vin import is_valid_vin

    valid = bool(is_valid_vin(req.vin))
    logger.info("vin_validate", extra={"vin_len": len(req.vin), "valid": valid})
    return VinResponse(vin=req.vin, valid=valid)


@app.middleware("http")
async def add_timing_header(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{elapsed_ms:.2f}ms"
    logger.info(
        "request",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "ms": round(elapsed_ms, 2),
        },
    )
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
