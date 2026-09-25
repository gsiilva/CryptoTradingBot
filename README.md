#  CryptoTradingBot

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Binance API](https://img.shields.io/badge/Binance-API-F0B90B?logo=binance&logoColor=black)](https://binance-docs.github.io/apidocs/)
[![Status](https://img.shields.io/badge/Status-Demo%20Trading-orange)](#disclaimer)

A modular algorithmic trading bot developed in Python, integrated with the official **Binance API**. The bot follows a clean, professional architecture that separates responsibilities (data, strategy, execution, and notifications) and is configured to run in both **Binance Demo Trading**, allowing you to test strategies without financial risk, and **Real Trading** environments.

---

##  Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Strategy](#-strategy)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Bot](#running-the-bot)
- [Email Notifications](#-email-notifications)
- [Disclaimer](#-disclaimer)

---

##  Features

- **Secure Connection** — Automated authentication and robust handling of API drops or network issues.
- **Integrated Strategy** — Uses Exponential Moving Average crossovers (EMA 9 and EMA 21) filtered by the Relative Strength Index (RSI 14) for decision-making.
- **Automatic Position Sizing** — Mathematically calculates trade sizes (e.g., investing 90% of the available balance, not recommended to switch to 100%) while strictly adhering to Binance's `LOT_SIZE` and decimal precision rules.
- **Email Notifications** — Sends HTML-formatted alerts (trade signals, order execution, errors) via a dedicated notifier module.
- **Modular Architecture** — Code is divided into independent modules, making it easy to test, maintain, and extend with new strategies.
- **Detailed Logging** — Built-in logging system for real-time monitoring of trades, signals, and errors.

---

##  Project Structure

```text
CryptoTradingBot/
│
├── config.py                 # Global settings and environment control (Demo/Real)
├── main.py                   # Orchestrator, main loop, and state management (Positioned/Flat)
│
├── core/
│   ├── connection.py         # Authentication and API ping testing
│   └── notifier.py           # Builds and sends email alerts (trades, errors, status)
│
├── data/
│   └── market.py             # Fetches historical klines (candles) and builds DataFrames
│
├── strategies/
│   └── rsi_ema.py            # The Brain: indicator math via pandas-ta and trade signals
│
├── execution/
│   └── orders.py             # The Hands: safe quantity calculation and Market Order execution
│
└── templates/
    └── email_alert.html      # HTML template used by notifier.py for email alerts
```

---

##  Strategy

The bot trades based on a trend-following signal confirmed by momentum:

| Indicator | Role |
|---|---|
| **EMA 9 / EMA 21** | Identifies short-term trend direction via crossover |
| **RSI 14** | Filters signals to avoid entries in overbought/oversold conditions |

A position is only opened when both the EMA crossover **and** the RSI filter agree, reducing false signals from trend reversals.

---

##  Getting Started

### Prerequisites

- Python 3.10+
- A Binance account with API keys generated for the **Demo Trading (Testnet)** environment
- `pip` for dependency management

### Installation

```bash
git clone https://github.com/<gsiilva>/CryptoTradingBot.git
cd CryptoTradingBot
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Credentials are read directly from **system environment variables** via `os.getenv()` — no `.env` file is used. On Windows, set the variables before running the bot

### Running the Bot

```bash
python main.py
```

The bot will authenticate, start monitoring the configured market, and log all signals, trades, and errors to the console (and optionally to a log file).

---

##  Email Notifications

The `core/notifier.py` module sends formatted HTML emails (rendered from `templates/email_alert.html`) for key events, such as:

-  Successful trade execution
-  Errors or connection issues
-  General status updates

---

## ️ Disclaimer

This project is intended for **educational and testing purposes only**. It is configured by default to run against Binance's **Demo Trading (Testnet)** environment. Trading cryptocurrencies involves substantial risk of loss. If you choose to run this bot against a real account, you do so **at your own risk** — the author assumes no responsibility for any financial losses.

