# Drow HTTP

Prometheus http query client of Python.

Implemented prometheus http api:
https://prometheus.io/docs/prometheus/latest/querying/api/

[![PyPI Version][pypi-badge]][pypi]
[![Build Status][qaci-badge]][qaci]

## install

    pip install drow-http

## usage

get client:

    from drow_http import get_client

    client = get_client("http://127.0.0.1:9090")

query as vector:

    result = client.query_as_vector("http_requests_total")
    for s in result.series:
        print(s.metric, s.value.timestamp, s.value.value)

query range:

    import time

    end = time.time()
    start = end - 60 * 60

    result = client.query_range("http_requests_total", start=start, end=end)
    for s in result.series:
        print(s.metric)
        for p in s.values:
            print(p.timestamp, p.value)

[pypi-badge]: https://img.shields.io/pypi/v/drow-http "PyPI Version"
[pypi]: https://pypi.org/project/drow-http "PyPI Version"
[qaci-badge]: https://img.shields.io/github/check-runs/xospc/drow-http/main "Build Status"
[qaci]: https://github.com/xospc/drow-http/actions "Build Status"
