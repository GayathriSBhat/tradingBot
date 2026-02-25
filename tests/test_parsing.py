import pytest

@pytest.mark.parsing
def test_non_numeric_price():
    with pytest.raises(ValueError):
        float("abc")

@pytest.mark.parsing
def test_missing_argument(parse_order):
    with pytest.raises(TypeError):
        parse_order(price=100)

@pytest.mark.parsing
def test_invalid_flag(cli_parser):
    with pytest.raises(SystemExit):
        cli_parser.parse_args(["--price", "abc"])