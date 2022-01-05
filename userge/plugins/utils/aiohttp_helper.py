# """
# Idea by @Pokurt
# Repo: https://github.com/pokurt/Nana-Remix/blob/master/nana/utils/aiohttp_helper.py
# """

import asyncio
from typing import Dict, Optional

import ujson
from aiohttp import ClientSession, ClientTimeout

# """
# Success: status == 200
# Failure: ValueError if status != 200 or timeout
# """


class AioHttp:
    @staticmethod
    def get_session() -> ClientSession:
        return ClientSession(json_serialize=ujson.dumps)

    @staticmethod
    async def _manage_session(
        mode: str,
        link: str,
        params: Optional[Dict] = None,
        session: Optional[ClientSession] = None,
    ):
        try:
            if session and not session.closed:
                return await AioHttp._request(
                    mode=mode, session=session, link=link, params=params
                )
            async with AioHttp.get_session() as xsession:
                return await AioHttp._request(
                    mode=mode, session=xsession, link=link, params=params
                )
        except asyncio.TimeoutError:
            print("Timeout! the site didn't responded in time.")
        except Exception as e:
            print(e)

    @staticmethod
    async def _request(mode: str, session: ClientSession, **kwargs):
        wait = 5 if mode == "status" else 15
        async with session.get(
            kwargs["link"], params=kwargs["params"], timeout=ClientTimeout(total=wait)
        ) as resp:
            if mode == "status":
                return resp.status
            if mode == "redirect":
                return resp.url
            if mode == "headers":
                return resp.headers
            # Checking response status
            if resp.status != 200:
                return False
            if mode == "json":
                r = await resp.json()
            elif mode == "text":
                r = await resp.text()
            elif mode == "read":
                r = await resp.read()
            return r

    @staticmethod
    async def json(
        link: str,
        params: Optional[Dict] = None,
        session: Optional[ClientSession] = None,
    ):
        res = await AioHttp._manage_session(
            mode="json", link=link, params=params, session=session
        )
        if not res:
            raise ValueError
        return res

    @staticmethod
    async def text(
        link: str,
        params: Optional[Dict] = None,
        session: Optional[ClientSession] = None,
    ):
        res = await AioHttp._manage_session(
            mode="text", link=link, params=params, session=session
        )
        if not res:
            raise ValueError
        return res

    @staticmethod
    async def read(
        link: str,
        params: Optional[Dict] = None,
        session: Optional[ClientSession] = None,
    ):
        res = await AioHttp._manage_session(
            mode="read", link=link, params=params, session=session
        )
        if not res:
            raise ValueError
        return res

    # Just returns the status
    @staticmethod
    async def status(link: str, session: Optional[ClientSession] = None):
        return await AioHttp._manage_session(mode="status", link=link, session=session)

    # returns redirect url
    @staticmethod
    async def redirect_url(link: str, session: Optional[ClientSession] = None):
        return await AioHttp._manage_session(
            mode="redirect", link=link, session=session
        )

    # Just returns the Header
    @staticmethod
    async def headers(
        link: str, session: Optional[ClientSession] = None, raw: bool = True
    ):
        headers_ = await AioHttp._manage_session(
            mode="headers", link=link, session=session
        )
        if headers_:
            if raw:
                return headers_
            text = ""
            for key, value in headers_.items():
                text += f"🏷 <i>{key}</i>: <code>{value}</code>\n\n"
            return f"<b>URl:</b> {link}\n\n<b>HEADERS:</b>\n\n{text}"