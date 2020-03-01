import json
import typing

from .datatypes import Address, Headers, QueryParams, URL
from .types import Scope, Receive, Send, Message


async def empty_receive() -> Message:
    raise RuntimeError("Receive channel has not been made available")

async def empty_send(message: Message) -> None:
    raise RuntimeError("Send channel has not been made available")


class HttpConnection:
    def __init__(self, scope: Scope) -> None:
        assert scope["type"] in ("http", "websocket")
        self.scope = scope

    def __getitem__(self, key: str) -> str:
        return self.scope[key]

    def __iter__(self) -> typing.Iterator[str]:
        return iter(self.scope)

    def __len__(self) -> int:
        return len(self.scope)

    @property
    def app(self) -> typing.Any:
        return self.scope["app"]

    @property
    def path(self) -> str:
        return self.scope["path"]

    @property
    def url(self) -> URL:
        if hasattr(self, "_url"):
            return self._url

        self._url = URL(self.scope)
        return self._url

    @property
    def headers(self) -> Headers:
        if hasattr(self, "_headers"):
            return self._headers

        self._headers = Headers(self.scope["headers"])
        return self._headers

    @property
    def query_params(self) -> QueryParams:
        if hasattr(self, "_query_params"):
            return self._query_params

        self._query_params = QueryParams(self.scope["query_string"])
        return self._query_params

    @property
    def session(self) -> dict:
        # TODO: implemnt session
        return None

    @property
    def cookie(self) -> typing.Dict[str, str]:
        # TODO: implement getting cookie
        return None

    @property
    def client(self) -> typing.Any:
        host, port = self.scope.get("client") or (None, None)
        if host:
            return Address(host, port)
        return None

    @property
    async def auth(self) -> typing.Any:
        # TODO: implement after authentication middleware
        pass

    @property
    async def user(self) -> typing.Any:
        # TODO: implement after authentication middleware
        pass


class Request(HttpConnection):
    def __init__(
        self,
        scope: Scope,
        receive: Receive = empty_receive,
        send: Send = empty_send,
    ):
        super().__init__(scope)
        self.receive = receive
        self.send = send

    @property
    def method(self) -> str:
        return self.scope["method"]

    @property
    def receive(self) -> Receive:
        return self.__receive

    @receive.setter
    def receive(self, receive: Receive):
        self.__receive = receive

    @property
    def send(self) -> Send:
        return self.__send

    @send.setter
    def send(self, send: Send):
        self.__send = send

    async def stream(self) -> bytes:
        if hasattr(self, "_body"):
            return self._body

        body = b''
        more_body = True

        while more_body:
            message = await self.receive()
            body += message.get('body', b'')
            more_body = message.get('more_body', False)

        return body

    async def body(self) -> bytes:
        if hasattr(self, "_body"):
            return self._body

        self._body = await self.stream()
        return self._body

    async def json(self) -> typing.Any:
        if not hasattr(self, "_json"):
            body = await self.body()
            self._json = {} if body.decode() == '' else json.loads(body)
        return self._json

    async def form(self) -> dict:
        # TODO: implement form data
        pass
