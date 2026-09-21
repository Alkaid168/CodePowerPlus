"""领域错误与 HTTP 映射。

业务代码只抛下面这些异常，接口层统一翻译成 ``{"code", "detail"}``；
前端只需要读 ``detail`` 显示原因、读 ``code`` 做分支处理。
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class DomainError(Exception):
    """业务规则不满足时的基类。"""

    status_code = 400
    code = 'bad_request'


class NotFound(DomainError):
    status_code = 404
    code = 'not_found'


class Conflict(DomainError):
    """并发或状态冲突，例如审核时发现分析已被替换。"""

    status_code = 409
    code = 'conflict'


class InvalidInput(DomainError):
    """语义校验失败，例如标签不在词表里、缺少证据。"""

    status_code = 422
    code = 'invalid_input'


class ModelUnavailable(DomainError):
    status_code = 503
    code = 'model_unavailable'


def _format_validation_error(exc: RequestValidationError) -> str:
    first = exc.errors()[0] if exc.errors() else {}
    location = '.'.join(str(part) for part in first.get('loc', ()) if part != 'body')
    message = first.get('msg', '请求参数不合法')
    return f'{location}: {message}' if location else message


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def _domain_error(_: Request, exc: DomainError):
        return JSONResponse(status_code=exc.status_code, content={'code': exc.code, 'detail': str(exc)})

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422,
                            content={'code': 'invalid_request', 'detail': _format_validation_error(exc)})
