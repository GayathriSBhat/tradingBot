import pytest


# ---------- API mocks ----------

class MockClientInvalidKey:
    def place_order(self):
        raise Exception("Authentication failed")


@pytest.fixture
def mock_client_invalid_key():
    return MockClientInvalidKey()


class MockServer500:
    def place_order(self):
        class Response:
            status_code = 500
        return Response()


@pytest.fixture
def mock_server_500():
    return MockServer500()


class MockTimeoutClient:
    def place_order(self):
        raise TimeoutError("Request timed out")


@pytest.fixture
def mock_timeout_client():
    return MockTimeoutClient()


# ---------- Client mocks ----------

class MockLowBalanceClient:
    def place_large_order(self):
        raise Exception("Insufficient balance")


@pytest.fixture
def mock_low_balance_client():
    return MockLowBalanceClient()


class MockPartialFill:
    def get_order_status(self):
        return "PARTIALLY_FILLED"


@pytest.fixture
def mock_partial_fill():
    return MockPartialFill()


class MockDuplicateOrder:
    def submit_twice(self):
        return "duplicate_detected"


@pytest.fixture
def mock_duplicate_order():
    return MockDuplicateOrder()


# ---------- Parsing mocks ----------

def dummy_parse_order(**kwargs):
    if "quantity" not in kwargs:
        raise TypeError("Missing argument")


@pytest.fixture
def parse_order():
    return dummy_parse_order


class DummyParser:
    def parse_args(self, args):
        raise SystemExit("Invalid flag")


@pytest.fixture
def cli_parser():
    return DummyParser()


# ---------- Response mocks ----------

def dummy_parse_response(resp):
    if "orderId" not in resp:
        raise KeyError("Missing orderId")


@pytest.fixture
def parse_response():
    return dummy_parse_response


def dummy_logger(path):
    with open(path, "w") as f:
        f.write("log")


@pytest.fixture
def logger_func():
    return dummy_logger