import time
from http import HTTPStatus

import psutil
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from server.log import get_logger

log = get_logger()


class AuditMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path not in ["/login"]:
            return await call_next(request)

        # record before request
        process = psutil.Process()
        start_time = time.perf_counter()
        start_cpu_thread = time.thread_time()
        memory_start = process.memory_info().rss / 1024 / 1024

        # running the request
        response = await call_next(request)

        # record after request
        latency_ms = (time.perf_counter() - start_time) * 1000
        memory_delta_mb = process.memory_info().rss / 1024 / 1024 - memory_start
        cpu_usage_ms = (time.thread_time() - start_cpu_thread) * 1000
        is_success = response.status_code == HTTPStatus.OK
        reason = "success" if is_success else request.state.failure_reason

        log.audit(
            username=request.state.username,
            password_score=getattr(request.state, "password_score", "N/A"),
            success=is_success,
            reason=reason,
            latency_ms=round(latency_ms, 3),
            cpu_usage_ms=round(cpu_usage_ms, 6),
            memory_delta_mb=round(memory_delta_mb, 3)
        )

        return response
