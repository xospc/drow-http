from decimal import Decimal
from typing import Optional, Any, Generic, TypeVar, ParamSpec, Concatenate
from collections.abc import Callable

from requests import Session

from drow.query import (
    RequestArg,
    build_arg_for_query,
    build_arg_for_query_range,
)
from drow.converter import Converter
from drow.parser import (
    QueryResponse,
    QueryRangeResponse,
    BaseParser,
    make_parser,
)

DEFAULT_USER_AGENT = "drow http client"
DEFAULT_TIMEOUT = 10

T = TypeVar("T")
P = ParamSpec("P")
DataType = TypeVar("DataType")
ModelType = TypeVar("ModelType")


def create_session(user_agent: str) -> Session:
    s = Session()
    s.headers.update({"User-Agent": user_agent})
    return s


class ApiClient:
    def __init__(
        self,
        base_url: str,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.base_url = base_url
        self.timeout = timeout

        self._session = create_session(user_agent)

    def _request(self, arg: RequestArg) -> Any:  # type: ignore[explicit-any]
        resp = self._session.get(
            url=arg.url,
            params=arg.params,
            timeout=self.timeout,
        )
        return resp.json()  # type: ignore[misc]

    def query(
        self, metric: str, time: Optional[float] = None,
    ) -> QueryResponse:
        arg = build_arg_for_query(self.base_url, metric, time)
        data: QueryResponse = self._request(arg)
        return data

    def query_range(
        self, metric: str, start: float, end: float,
        step: Optional[float] = None, step_count: int = 60
    ) -> QueryRangeResponse:
        arg = build_arg_for_query_range(
            self.base_url, metric,
            start=start, end=end,
            step=step, step_count=step_count,
        )
        data: QueryRangeResponse = self._request(arg)
        return data


def _wrap_parser(
    parse: Callable[[BaseParser[T], DataType], ModelType],
    fetch: Callable[Concatenate[ApiClient, P], DataType]
) -> Callable[Concatenate["PrometheusClient[T]", P], ModelType]:
    def inner(
        self: "PrometheusClient[T]", /, *args: P.args, **kwargs: P.kwargs,
    ) -> ModelType:
        return parse(self.parser, fetch(self.client, *args, **kwargs))

    return inner


def _wrap_creator(
    converter: Converter[T],
    client_creator: Callable[P, ApiClient],
) -> Callable[P, "PrometheusClient[T]"]:
    def inner(
        *args: P.args, **kwargs: P.kwargs,
    ) -> PrometheusClient[T]:
        api_client = client_creator(*args, **kwargs)
        parser = make_parser(converter)
        return PrometheusClient(api_client, parser)

    return inner


class PrometheusClient(Generic[T]):
    def __init__(self, client: ApiClient, parser: BaseParser[T]):
        self.client = client
        self.parser = parser

    query = _wrap_parser(
        BaseParser.parse_query_response,
        ApiClient.query,
    )
    query_range = _wrap_parser(
        BaseParser.parse_query_range_response,
        ApiClient.query_range,
    )
    query_as_vector = _wrap_parser(
        BaseParser.parse_query_response_as_vector,
        ApiClient.query,
    )
    query_as_value = _wrap_parser(
        BaseParser.parse_query_response_as_value,
        ApiClient.query,
    )
    query_as_value_point = _wrap_parser(
        BaseParser.parse_query_response_as_value_point,
        ApiClient.query,
    )


get_client = _wrap_creator(Decimal, ApiClient)
