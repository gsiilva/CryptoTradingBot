import pandas as pd
import logging

def buscar_dados_historicos(client, symbol, interval, limit=1000):
    try:
        logging.info(f"Buscando os ultimos {limit} dados historicos para {symbol} no intervalo {interval}")

        # requisicao dados brutos
        klines = client.get_historical_klines(symbol=symbol, interval=interval, limit=limit)
        colunas = [
            'timestamp', 'open', 'high', 'low', 'close',
            'volume', 'close_time', 'quote_asset_volume',
            'number_of_trades', 'taker_buy_base_asset_volume',
            'taker_buy_quote_asset_volume', 'ignore'
        ]

        # converte da lista em um dataframe (tabela) estruturado
        df = pd.DataFrame(klines, columns=colunas)

        # mantem apenas as colunas uteis das 12 q vem
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

        colunas_numericas = ['open', 'high', 'low', 'close', 'volume']

        df[colunas_numericas] = df[colunas_numericas].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

        logging.info("Dados de mercado estruturados")
        return df

    except Exception as e:
        logging.error(f"Erro ao buscar dados do mercado: {e}")
        return None


if __name__ == "__main__":
    import sys
    import os

    # Adiciona a pasta raiz ao sistema para conseguir importar a pasta core
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.connection import conectar_binance

    # Configura o log básico para o teste
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    cliente = conectar_binance()
    if cliente:
        # Testa buscando os últimos 5 candles de 15 minutos do Bitcoin
        tabela_precos = buscar_dados_historicos(cliente, symbol="BTCUSDT", interval="15m", limit=5)

        if tabela_precos is not None:
            print("\nÚltimos preços processados:")
            print(tabela_precos)