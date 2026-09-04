import pandas as pd
import pandas_ta as ta
import logging


def analisar_mercado(df):
    """
    Recebe um DataFrame com o histórico de preços, calcula os indicadores
    e retorna o sinal de negociação para o momento atual.

    Retornos possíveis: "COMPRAR", "VENDER" ou "AGUARDAR"
    """
    try:
        # 1. Calcular os indicadores e criar novas colunas
        df['ema_rapida'] = ta.ema(df['close'], length=9)
        df['ema_lenta'] = ta.ema(df['close'], length=21)
        df['rsi'] = ta.rsi(df['close'], length=14)

        # Removemos as linhas iniciais que não têm dados suficientes para o cálculo
        df.dropna(inplace=True)

        # 2. Pegar os dois últimos candles fechados para verificar cruzamentos
        candle_atual = df.iloc[-1]
        candle_anterior = df.iloc[-2]

        # 3. Lógica de Compra (Golden Cross + RSI saudável)
        cruzou_pra_cima = (candle_anterior['ema_rapida'] <= candle_anterior['ema_lenta']) and \
                          (candle_atual['ema_rapida'] > candle_atual['ema_lenta'])
        rsi_saudavel = candle_atual['rsi'] < 70

        if cruzou_pra_cima and rsi_saudavel:
            logging.info(f"SINAL DE COMPRA! EMA 9 cruzou EMA 21 para cima. RSI: {candle_atual['rsi']:.2f}")
            return "COMPRAR"

        # 4. Lógica de Venda (Death Cross)
        cruzou_pra_baixo = (candle_anterior['ema_rapida'] >= candle_anterior['ema_lenta']) and \
                           (candle_atual['ema_rapida'] < candle_atual['ema_lenta'])

        if cruzou_pra_baixo:
            logging.info(f"SINAL DE VENDA! EMA 9 cruzou EMA 21 para baixo.")
            return "VENDER"

        # Se não cruzou para nenhum dos lados, apenas seguimos aguardando
        return "AGUARDAR"

    except Exception as e:
        logging.error(f"Erro ao analisar o mercado e calcular indicadores: {e}")
        return "AGUARDAR"


# Teste isolado do módulo
if __name__ == "__main__":
    import sys
    import os

    # Configuração para conseguir importar as outras pastas
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.connection import conectar_binance
    from data.market import buscar_dados_historicos

    logging.basicConfig(level=logging.INFO, format='%(message)s')

    cliente = conectar_binance()
    if cliente:
        # Precisamos de pelo menos uns 30 candles para a EMA de 21 funcionar
        tabela = buscar_dados_historicos(cliente, "BTCUSDT", "15m", 50)

        if tabela is not None:
            sinal = analisar_mercado(tabela)
            print(f"\nSinal atual para BTCUSDT: {sinal}")