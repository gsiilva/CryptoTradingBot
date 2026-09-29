import logging

import pandas_ta as ta


def analisar_mercado(df, rsi_compra_min=40, rsi_compra_max=65):
    """Retorna COMPRAR/VENDER/AGUARDAR usando apenas candles fechados."""
    try:
        if df is None or len(df) < 22:
            return "AGUARDAR"

        # Evita alterar o DataFrame recebido pelo chamador.
        dados = df.copy()
        dados["ema_rapida"] = ta.ema(dados["close"], length=9)
        dados["ema_lenta"] = ta.ema(dados["close"], length=21)
        dados["rsi"] = ta.rsi(dados["close"], length=14)
        dados = dados.dropna(subset=["ema_rapida", "ema_lenta", "rsi"])
        if len(dados) < 2:
            return "AGUARDAR"

        atual, anterior = dados.iloc[-1], dados.iloc[-2]
        cruzou_alta = anterior["ema_rapida"] <= anterior["ema_lenta"] and atual["ema_rapida"] > atual["ema_lenta"]
        cruzou_baixa = anterior["ema_rapida"] >= anterior["ema_lenta"] and atual["ema_rapida"] < atual["ema_lenta"]
        rsi_confirma = rsi_compra_min <= atual["rsi"] <= rsi_compra_max and atual["rsi"] > anterior["rsi"]

        if cruzou_alta and rsi_confirma:
            logging.info("Sinal de compra: cruzamento EMA de alta e RSI confirmando (%.2f).", atual["rsi"])
            return "COMPRAR"
        if cruzou_baixa:
            logging.info("Sinal de venda: cruzamento EMA de baixa.")
            return "VENDER"
        return "AGUARDAR"
    except Exception:
        logging.exception("Erro ao analisar o mercado")
        return "AGUARDAR"
