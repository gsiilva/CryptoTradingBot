import os

API_KEY = os.getenv("BINANCE_API_KEY_REAL")
API_SECRET = os.getenv("BINANCE_API_SECRET_REAL")

USE_DEM0 = False

SENDER_EMAIL = os.getenv("BOT_EMAIL_ADRESS")
SENDER_PASSWORD = os.getenv("BOT_16_PASSWORD")
RECEIVER_EMAIL = os.getenv("PERSONAL_EMAIL")

if __name__ == "__main__":
    print(SENDER_EMAIL)
    print(SENDER_PASSWORD)