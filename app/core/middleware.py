import time

from starlette.middleware.base import BaseHTTPMiddleware

from .logger import logger


class RequestLoggingMiddleware(
    BaseHTTPMiddleware
):

    async def dispatch(
        self,
        request,
        call_next
    ):

        start_time = time.time()

        logger.info(
            f"REQUEST STARTED: "
            f"{request.method} {request.url.path}"
        )

        response = await call_next(request)

        process_time = (
            time.time() - start_time
        )

        logger.info(
            f"REQUEST COMPLETED: "
            f"{request.method} {request.url.path} | "
            f"STATUS: {response.status_code} | "
            f"TIME: {process_time:.4f}s"
        )

        response.headers[
            "X-Process-Time"
        ] = str(process_time)

        return response