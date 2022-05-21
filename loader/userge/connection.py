__all__ = ['send_and_wait', 'send_and_async_wait']

import asyncio
import atexit
from threading import Lock


_LOCK = Lock()
_A_LOCK = asyncio.Lock()


def send_and_wait(*_):
    with _LOCK:
        _send(*_)
        return _recv()


async def send_and_async_wait(*_):
    async with _A_LOCK:
        with _LOCK:
            _send(*_)
            while not _poll():
                await asyncio.sleep(0.5)
            return _recv()


def _send(*_) -> None:
    if _poll():
        raise Exception("connection is being used!")
    _Conn.send(_)


def _recv():
    result = _Conn.recv()
    if isinstance(result, Exception):
        raise result
    return result


def _poll() -> bool:
    return _Conn.poll()


def _set(conn) -> None:
    _Conn.set(conn)


class _Conn:
    _instance = None

    @classmethod
    def set(cls, conn) -> None:
        if cls._instance:
            cls._instance.close()
        cls._instance = conn

    @classmethod
    def _get(cls):
        if not cls._instance:
            raise Exception("connection not found!")
        if cls._instance.closed:
            raise Exception("connection has been closed!")
        return cls._instance

    @classmethod
    def send(cls, _) -> None:
        cls._get().send(_)

    @classmethod
    def recv(cls):
        return cls._get().recv()

    @classmethod
    def poll(cls) -> bool:
        return cls._get().poll()

    @classmethod
    def close(cls) -> None:
        if cls._instance:
            cls._instance.close()
            cls._instance = None


atexit.register(_Conn.close)
