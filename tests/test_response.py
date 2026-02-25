import pytest

@pytest.mark.response
def test_missing_field_in_response(parse_response):
    bad_response = {"status": "FILLED"}  # missing fields

    with pytest.raises(KeyError):
        parse_response(bad_response)

@pytest.mark.response
def test_logging_file_written(tmp_path, logger_func):
    log_file = tmp_path / "app.log"
    logger_func(log_file)

    assert log_file.exists()

@pytest.mark.response
def test_unexpected_schema(parse_response):
    weird_response = {"foo": "bar"}

    with pytest.raises(Exception):
        parse_response(weird_response)