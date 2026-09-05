from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from binance.exceptions import BinanceAPIException
import logging

from numpy.ma.core import logical_or

from core import connection

def executar_ordem(client, symbol, side, quantity):
    """
    Envia uma ordem do mercado para a corretora
    :param client: Objeto de conexão da Binance
    :param symbol: O par de moedas (ex: 'BTCUSDT')
    :param side: Direção da ordem (SIDE_BUY ou SIDE_SELL)
    :param quantity: Quantidade da moeda a ser negociada
    :return: Dicionário com os detalhes da ordem executada ou None em caso de erro
    """

    try:
        direcao = "COMPRA" if side == SIDE_BUY else "VENDA"
        logging.info(f"Executando ordem {symbol}...")

        ordem = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )

        logging.info(f"Ordem {symbol} executado com sucesso!")
        return ordem

    except BinanceAPIException as e:
        logging.error(f"Erro na Binance API: {e.message}")
        return None
    except BinanceAPIException as e:
        logging.error(f"Erro inesperado: {e.message}")
        return None


if __name__ == "__main__":
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.connection import conectar_binance

    logging.basicConfig(level=logging.INFO, format='%(message)s')

    cliente = conectar_binance()
    if cliente:
        # ATENÇÃO: A Binance é rígida com a quantidade (LOT_SIZE).
        # O Bitcoin, por exemplo, exige no mínimo 0.001 ou 0.0001 dependendo do par.
        # Vamos tentar comprar uma pequena quantidade para testar.

        simbolo_teste = "BTCUSDT"
        quantidade_teste = 0.009  # Ajuste conforme o saldo da sua conta Demo

        print(f"\n--- Iniciando Teste de Ordem na Conta Demo ---")
        # Envia a ordem de compra
        resultado = executar_ordem(cliente, simbolo_teste, SIDE_BUY, quantidade_teste)

        if resultado:
            print("\nDetalhes completos devolvidos pela Binance:")
            print(resultado)
