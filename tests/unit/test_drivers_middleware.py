from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request
from app.drivers.api.middleware import LoggingMiddleware, BodyCapturingReceive, ResponseCapturingWrapper


def test_body_capturing_receive():
    receive_mock = AsyncMock()
    receive_mock.return_value = {
        "type": "http.request",
        "body": b"test body",
        "more_body": False
    }
    
    capturer = BodyCapturingReceive(receive_mock)
    
    import asyncio
    result = asyncio.run(capturer())
    
    assert capturer.get_body() == b"test body"


def test_body_capturing_receive_multiple_chunks():
    receive_mock = AsyncMock()
    receive_mock.side_effect = [
        {"type": "http.request", "body": b"chunk1", "more_body": True},
        {"type": "http.request", "body": b"chunk2", "more_body": False}
    ]
    
    capturer = BodyCapturingReceive(receive_mock)
    
    import asyncio
    asyncio.run(capturer())
    asyncio.run(capturer())
    
    assert capturer.get_body() == b"chunk1chunk2"


def test_body_capturing_receive_reset():
    receive_mock = AsyncMock()
    capturer = BodyCapturingReceive(receive_mock)
    
    capturer.reset()
    
    assert capturer._current_index == 0


def test_response_capturing_wrapper():
    from starlette.responses import Response
    
    response_mock = Response(content=b"test content")
    
    wrapper = ResponseCapturingWrapper(response_mock)
    
    assert wrapper.response == response_mock


def test_logging_middleware_init():
    app_mock = Mock()
    middleware = LoggingMiddleware(app_mock)
    
    assert middleware.app == app_mock

