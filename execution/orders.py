from binance.enums import SIDE_BUY, SIDE_SELL, ORDER_TYPE_MARKET
from binance.exceptions import BinanceAPIException
import logging
import math

from numpy.ma.core import logical_or

from core import connection

def obter_saldo(client, ativo):
    """
    Pega o saldo disponivel referente ao ativo
    """
    try:
        conta = client.get_account()
        for balance in conta['balances']:
            if balance['asset'] == ativo:
                return float(balance['free'])
        return 0.0
    except Exception as e:
        logging.error(f"Erro ao buscar saldo do ativo: {e.message}")
        return 0.0

def calcular_quantidade(client, symbol, ativo_base, ativo_cotacao, percentual=0.90):
    """
    Calcula a quantidade permitida pela binance para comprar e vender
    PARA COMPRA: Usa o percentual definido
    PARA VENDA: Usa 100% do ativo base
    """
    try:
        info = client.get_symbol_info(symbol)
        step_size = 0.00001 # valor padrao por seguranca

        for filter in info['filters']:
            if filter['filterType'] == 'LOT_SIZE':
                step_size = float(filter['stepSize'])
                break

        casas_decimais = max(0, int(round(-math.log10(step_size))))
        fator_truncamento = 10 ** casas_decimais

        if percentual > 0: # logica pra compra, compra 90%
            saldo_dolar = obter_saldo(client, ativo_cotacao)
            valor_investir = saldo_dolar * percentual

            ticker = client.get_symbol_ticker(symbol=symbol)
            preco_atual = float(ticker['price'])

            quantidade_bruta = valor_investir / preco_atual

        else: # logica pra venda, vende 100%
            quantidade_bruta = obter_saldo(client, ativo_base)

        quantidade_final = math.floor(quantidade_bruta * fator_truncamento) / fator_truncamento
        return quantidade_final

    except Exception as e:
        logging.error(f"Erro ao calcular quantidade: {e.message}")


def executar_ordem(client, symbol, side, quantity):
    """
    Envia a ordem a mercado para a corretora.
    """
    try:
        if quantity <= 0:
            logging.warning("Quantidade calculada é zero. Ordem cancelada.")
            return None

        direcao = "COMPRA" if side == SIDE_BUY else "VENDA"
        logging.info(f"Preparando ordem de {direcao} de {quantity} {symbol} a mercado...")

        ordem = client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )

        logging.info(f"Ordem executada com sucesso! ID da Ordem: {ordem['orderId']}")
        return ordem

    except BinanceAPIException as e:
        logging.error(f"Erro na corretora ao executar ordem: {e.status_code} - {e.message}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado ao enviar ordem: {e}")
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
