"""Keep the default suite offline; real source checks require explicit opt-in."""

import socket

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-network", action="store_true", default=False, help="Run marked network tests."
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "network: opt-in real dataset/network integration")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-network"):
        skip = pytest.mark.skip(reason="Requires explicit --run-network opt-in")
        for item in items:
            if item.get_closest_marker("network"):
                item.add_marker(skip)


@pytest.fixture(autouse=True)
def offline_sockets(request, monkeypatch):
    if request.node.get_closest_marker("network") and request.config.getoption("--run-network"):
        return

    def blocked(*args, **kwargs):
        raise AssertionError("Network disabled: use @pytest.mark.network and --run-network")

    monkeypatch.setattr(socket, "socket", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(socket, "getaddrinfo", blocked)
