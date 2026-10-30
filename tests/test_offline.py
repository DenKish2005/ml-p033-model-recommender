"""Regression checks for accidental network use in the default suite."""

import socket

import pytest


@pytest.mark.parametrize(
    "operation",
    [
        lambda: socket.socket(),
        lambda: socket.create_connection(("example.invalid", 443)),
        lambda: socket.getaddrinfo("example.invalid", 443),
    ],
    ids=["socket", "connection", "dns"],
)
def test_default_suite_blocks_network(operation):
    with pytest.raises(AssertionError, match="Network disabled"):
        operation()
