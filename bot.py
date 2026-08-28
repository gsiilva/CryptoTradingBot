from binance.client import Client
from binance.exceptions import BinanceAPIException
import os

API_KEY = os.getenv("BINANCE_API_KEY_DEMO")
API_SECRET = os.getenv("BINANCE_API_KEY_SECRET")

if not API_KEY or not API_SECRET:
    raise RuntimeError("Chaves da Binance não configuradas.")

try:
    client = Client(API_KEY, API_SECRET, demo=True)

    client.ping()
    print("Connected")

    conta = client.get_account()

    print("Account info:")
    for ativo in conta["balances"]:
        if float(ativo['free']) > 0 or float(ativo['locked']) > 0:
            print(f"Moeda: {ativo['asset']} | Livre: {ativo['free']} | Bloqueado: {ativo['locked']}")

except BinanceAPIException as e:
    print(f"erro de API: {e.message}")
except Exception as e:
    print(f"erro inesperado: {e}")