# Binance Futures Trading Bot

## Overview

Simple CLI app to place and validate orders on Binance Futures Testnet.

---

## Features

- Supports `MARKET` and `LIMIT` orders  
- Validates orders against Binance trading rules  
- Logs requests and responses to console and file  

---

## How to Run (Docker version)

### 1. Clone the repository

```bash
git clone https://github.com/GayathriSBhat/tradingBot.git
cd tradingBot
```

### 2.  Create a .env file in the project root and add the following credentials:
```
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BASE_URL=https://testnet.binancefuture.com
```

### 3. Build Docker Image (One-Time)
```
docker build -t tradebot .
```

### 4. Create Container & Load Env Variables (One-Time Setup)
```
docker run -it --env-file .env --name tradebot tradebot
```

### 5. Once the CLI starts, you can stop it anytime using:
```
docker stop tradebot
```

### 6. Running the Bot Later
```
docker start -ai tradebot
```

---

## How to Run (Without Docker)

### 1. Install requirements
``` 
pip install -r requirements.txt
```

### 2. It's an interactive CLI App, so you don't need to worry about flags, just keep passing the values
```
python cli.py
```

---

## Example Usage

## Market Order
Symbol: BTCUSDT <br>
Side: BUY <br>
Order Type: MARKET <br>
Quantity: 0.003 <br>

## Limit Order
Symbol: BTCUSDT <br>
Side: SELL <br>
Order Type: LIMIT <br>
Quantity: 0.003 <br>
Price: 67000 <br>

---

## Testing

```
pytest tests/
```
---

## Assumptions

Uses Binance Futures Testnet

Requires API keys from https://testnet.binancefuture.com

## License

This project is licensed under the MIT License. See the LICENSE file for details.
