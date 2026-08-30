from binance.client import Client
from binance.exceptions import BinanceAPIException
import config
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt='%d/%m/%Y %H:%M:%S'
)

def conectar_binance():
    try:
        ambiente = "Demo" if config.USE_DEM0 else "Real"
        logging.info(f"Tentando conectar com a API (Ambiente: {ambiente})")

        client = Client(api_key=config.API_KEY, api_secret=config.API_SECRET, demo=config.USE_DEM0)
        client.ping()
        logging.info("Conectado com sucesso!")

        return client

    except BinanceAPIException as ex:
        logging.error(f"Erro na API da Binance: {ex}")
        return None
    except Exception as ex:
        logging.error(f"Erro inesperado: {ex}")
        return None

if __name__ == "__main__":
    client_test = conectar_binance()

    if client_test:
        status = client_test.get_system_status()
        logging.info(status)