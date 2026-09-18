# main.py

import time
import logging
from binance.enums import SIDE_BUY, SIDE_SELL

import config
from core.connection import conectar_binance
from core.notifier import enviar_email
from data.market import buscar_dados_historicos
from strategies.rsi_ema import analisar_mercado
from execution.orders import calcular_quantidade, executar_ordem

# Configuração global de log do bot
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def main():
    logging.info("Iniciando o Bot")

    # 1. Estabelece a conexão
    cliente = conectar_binance()
    if not cliente:
        logging.error("Falha crítica ao conectar com a Binance. Encerrando o bot.")
        return

    # Parâmetros de operação
    simbolo = "SOLUSDT"
    ativo_base = "SOL"
    ativo_cotacao = "USDT"
    intervalo_candle = "15m"
    quantidade_candles = 50  # O suficiente para a EMA de 21 calcular

    tempo_espera_segundos = 60  # Roda o loop a cada 1 minuto

    # Variável de estado: O bot começa sem posição (zerado)
    comprado = False

    logging.info(f"Bot em execução. Par: {simbolo} | Gráfico: {intervalo_candle} | Checagem: {tempo_espera_segundos}s")

    # 2. O Loop Infinito (Coração do Bot)
    while True:
        try:
            # Busca o DataFrame de preços
            df = buscar_dados_historicos(cliente, simbolo, intervalo_candle, quantidade_candles)

            if df is not None:
                # Envia para a estratégia decidir
                sinal = analisar_mercado(df)

                # 3. Execução das ordens baseada no sinal e no estado atual
                if sinal == "COMPRAR":
                    if not comprado:
                        logging.info("Sinal de COMPRA confirmado. Calculando tamanho da mão...")
                        # Calcula 90% do saldo em dólar
                        qtd = calcular_quantidade(cliente, simbolo, ativo_base, ativo_cotacao, percentual=0.90)

                        ordem = executar_ordem(cliente, simbolo, SIDE_BUY, qtd)
                        if ordem:
                            comprado = True

                            mensagem = f"COMPRA DE {qtd} {simbolo} REALIZADA!\nID DA ORDEM {ordem['orderId']}"
                            enviar_email(f"✅COMPRA EXECUTADA: {simbolo}", mensagem)
                    else:
                        logging.info("Sinal de COMPRA mantido, mas o bot já está posicionado. Ignorando.")

                elif sinal == "VENDER":
                    if comprado:
                        logging.info("Sinal de VENDA confirmado. Liquidando posição...")
                        # Passa percentual=0 para vender 100% do saldo em BTC
                        qtd = calcular_quantidade(cliente, simbolo, ativo_base, ativo_cotacao, percentual=0)

                        ordem = executar_ordem(cliente, simbolo, SIDE_SELL, qtd)
                        if ordem:
                            comprado = False

                            mensagem = f"VENDA DE {qtd} {simbolo} REALIZADA!\nID DA ORDEM {ordem['orderId']}"
                            enviar_email(f"✅VENDA EXECUTADA: {simbolo}", mensagem)
                    else:
                        logging.info("Sinal de VENDA mantido, mas o bot já está zerado. Ignorando.")

                else:
                    logging.info(f"Mercado lateral ou sem setup. Estado atual: {'Comprado' if comprado else 'Zerado'}.")

            # Pausa até a próxima checagem
            time.sleep(tempo_espera_segundos)

        except Exception as e:
            logging.error(f"Erro no loop principal: {e}")

            mensagem = f"ERRO NO LOOP PRINCIPAL: {e}!\nRECOMENDADO DESLIGAMENTO!"
            enviar_email("❌ERRO NO LOOP PRINCIPAL", mensagem)
            # Em caso de erro (ex: queda rápida de internet), espera 1 minuto e tenta de novo
            time.sleep(60)


if __name__ == "__main__":
    main()