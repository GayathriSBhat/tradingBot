# Binance Futures Trading Bot

## Overview

This project is a command-line application for placing and validating orders on Binance Futures. It includes features for market and limit orders, input validation, and logging. The bot is built using Python and leverages the Binance API for order placement.

---

## Features

- **Order Placement**: Supports `MARKET` and `LIMIT` orders.
- **Validation**: Validates orders against Binance trading rules (e.g., minimum notional, price tick size, lot size).
- **Logging**: Logs all requests and responses to a file and console.
- **Error Handling**: Handles API errors, invalid inputs, and other exceptions gracefully.
- **Mock Testing**: Includes unit tests with mock objects for API and client behavior.

---


## How to run?

Run the CLI to place an order:

### Market Orders

```bash
python cli.py \
    --symbol BTCUSDT \
    --side BUY \
    --order-type MARKET \
    --quantity 0.004 \
    --debug
```

```bash
python cli.py \
    --symbol BTCUSDT \
    --side SELL \
    --order-type MARKET \
    --quantity 0.004 \
    --debug
```

### Limit Orders

```bash
python cli.py \
    --symbol BTCUSDT \
    --side BUY \
    --order-type LIMIT \
    --quantity 0.004 \
    --price 30000 \
    --debug
```

```bash
python cli.py \
    --symbol BTCUSDT \
    --side SELL \
    --order-type LIMIT \
    --quantity 0.004 \
    --price 30000 \
    --debug
```

### Arguments

- `--symbol`: Trading pair (e.g., `BTCUSDT`).
- `--side`: Order side (`BUY` or `SELL`).
- `--order-type`: Order type (`MARKET` or `LIMIT`).
- `--quantity`: Order quantity.
- `--price`: Price for `LIMIT` orders (optional for `MARKET` orders).
- `--debug`: Enable debug logging.

---

## Testing

Run the test suite using `pytest`:

```bash
pytest
```

Test categories:

- **API Tests**: Validate API interactions.
- **Client Tests**: Test client behavior with mock objects.
- **Parsing Tests**: Ensure input validation works as expected.
- **Response Tests**: Verify response handling and logging.

---


---

## Best Practices

- **Validate Inputs**: Ensure all inputs meet Binance trading rules.
- **Handle Errors**: Gracefully handle API errors and invalid inputs.
- **Secure Secrets**: Keep API keys and secrets in the `.env` file.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Binance API Documentation](https://binance-docs.github.io/apidocs/futures/en/)
- [Typer](https://typer.tiangolo.com/) for building the CLI.
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation.

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
