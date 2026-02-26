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

## Binance Futures Order Constraints

### 1. Minimum Notional Requirement

Orders must meet a minimum value threshold.

**Rule:**
```
price × quantity ≥ minimum notional (typically around 100 USDT)
```

**Why it exists:**
- Prevents very small "dust" trades
- Reduces unnecessary load on the exchange

### 2. Price Band Restrictions

Limit order prices must remain within an acceptable range relative to the current market (mark price).

**Rules:**
- SELL limit orders cannot be far below market price.
- BUY limit orders cannot be far above market price.

**Why it exists:**
- Prevents manipulation
- Avoids accidental executions

### 3. Quantity Precision

Each trading pair defines a step size for quantity.

---

## How to Run

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
    --price 25000 \
    --quantity 0.004 \
    --debug
```

---

## Testing

Unit tests are included to validate the functionality of the bot. To run the tests, use:

```bash
pytest tests/
```

---

## Directory Structure

- `bot/`: Core logic for order placement, validation, and logging.
- `logs/`: Stores log files for debugging and tracking.
- `tests/`: Contains unit tests for the bot.

---

## Requirements

Install the required dependencies using:

```bash
pip install -r requirements.txt
```

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.
