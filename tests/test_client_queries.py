import pytest

@pytest.mark.client
def test_insufficient_balance(mock_low_balance_client):
    with pytest.raises(Exception):
        mock_low_balance_client.place_large_order()

@pytest.mark.client
def test_partial_fill_handling(mock_partial_fill):
    status = mock_partial_fill.get_order_status()
    assert status in ["PARTIALLY_FILLED", "FILLED"]

@pytest.mark.client
def test_duplicate_order_detection(mock_duplicate_order):
    result = mock_duplicate_order.submit_twice()
    assert result == "duplicate_detected"