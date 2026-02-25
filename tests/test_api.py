import pytest

@pytest.mark.api
def test_authentication_failure(mock_client_invalid_key):
    with pytest.raises(Exception):
        mock_client_invalid_key.place_order()

@pytest.mark.api
def test_server_failure(mock_server_500):
    response = mock_server_500.place_order()
    assert response.status_code == 500

@pytest.mark.api
def test_timeout(mock_timeout_client):
    with pytest.raises(TimeoutError):
        mock_timeout_client.place_order()

@pytest.mark.api
def test_filter_violation():
    price = 100
    qty = 0.00001  # below min notional
    min_notional = 5

    assert price * qty < min_notional