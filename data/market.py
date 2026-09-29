import logging

import pandas as pd


def buscar_dados_historicos(client, symbol, interval, limit=1000):
    try:
        klines = client.get_historical_klines(symbol=symbol, interval=interval, limit=limit)
        columns = ["timestamp", "open", "high", "low", "close", "volume", "close_time",
                   "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume",
                   "taker_buy_quote_asset_volume", "ignore"]
        df = pd.DataFrame(klines, columns=columns)
        if df.empty:
            return df

        df = df[["timestamp", "open", "high", "low", "close", "volume", "close_time"]].copy()
        numeric = ["open", "high", "low", "close", "volume"]
        df[numeric] = df[numeric].astype(float)
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)

        # A API inclui a vela em formação. Ela não pode participar dos sinais.
        agora = pd.Timestamp.now(tz="UTC")
        df = df.loc[df["close_time"] < agora].drop(columns=["close_time"]).reset_index(drop=True)
        return df
    except Exception:
        logging.exception("Erro ao buscar dados de mercado para %s", symbol)
        return None
