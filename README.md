#  Binance CryptoBot (Python)

A modular algorithmic trading bot developed in Python, integrated with the official Binance API. The bot features a professional architecture that separates responsibilities (data, strategy, and execution) and is configured to run in the Binance **Demo Trading** environment, allowing you to test strategies without financial risk.

##  Features

- **Secure Connection:** Automated authentication and robust handling of API drops or network issues.
- **Integrated Strategy:** Uses Exponential Moving Average crossovers (EMA 9 and EMA 21) filtered by the Relative Strength Index (RSI 14) for decision-making.
- **Automatic Position Sizing:** Mathematically calculates trade sizes (e.g., investing 90% of the available balance) while strictly adhering to Binance's `LOT_SIZE` and decimal precision rules.
- **Modular Architecture:** Code is divided into independent modules, making it easier to test, maintain, and implement new strategies in the future.
- **Detailed Logging:** Built-in logging system for real-time monitoring of trades, signals, and errors.

##  Project Structure

```text
crypto_bot/
│
├── config.py           # Global settings and environment control (Demo/Real)
├── main.py             # Orchestrator, main loop, and state management (Positioned/Flat)
│
├── core/
│   └── connection.py   # Authentication and API ping testing
│
├── data/
│   └── market.py       # Fetches historical klines (candles) and builds DataFrames
│
├── strategies/
│   └── rsi_ema.py      # The Brain: indicator math via pandas-ta and trade signals
│
└── execution/
    └── orders.py       # The Hands: safe quantity calculation and Market Order execution
