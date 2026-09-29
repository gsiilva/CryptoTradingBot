import json
import logging
import os
import time
from pathlib import Path

from binance.enums import SIDE_BUY, SIDE_SELL

import config
from core.connection import conectar_binance
from core.notifier import enviar_email
from data.market import buscar_dados_historicos
from execution.orders import (calcular_quantidade, executar_ordem, obter_minimo_notional,
                              obter_saldo, preco_medio_execucao)
from strategies.rsi_ema import analisar_mercado

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

SYMBOL = "ZECUSDT"
BASE_ASSET = "ZEC"
QUOTE_ASSET = "USDT"
INTERVAL = "15m"
CANDLE_COUNT = 100
POLL_SECONDS = 60
STATE_FILE = Path(__file__).with_name("bot_state.json")


def carregar_estado():
    try:
        if STATE_FILE.exists():
            with STATE_FILE.open("r", encoding="utf-8") as state_file:
                return json.load(state_file)
    except (OSError, json.JSONDecodeError):
        logging.exception("Não foi possível ler %s", STATE_FILE)
    return {"in_position": False, "entry_price": None, "quantity": 0.0, "last_candle": None}


def salvar_estado(state):
    temporary_file = STATE_FILE.with_suffix(".tmp")
    with temporary_file.open("w", encoding="utf-8") as state_file:
        json.dump(state, state_file, ensure_ascii=False, indent=2)
    os.replace(temporary_file, STATE_FILE)


def main():
    logging.info("Iniciando bot para %s (%s). Demo=%s", SYMBOL, INTERVAL, config.USE_DEM0)
    client = conectar_binance()
    if not client:
        logging.error("Falha ao conectar à Binance; encerrando.")
        return

    state = carregar_estado()
    try:
        base_balance = obter_saldo(client, BASE_ASSET)
        state_quantity = float(state.get("quantity") or 0)
        if base_balance <= 0 and state.get("in_position"):
            logging.warning("Estado indicava posição, mas saldo livre de %s está zerado; limpando estado.", BASE_ASSET)
            state.update(in_position=False, entry_price=None, quantity=0.0)
        elif base_balance > 0 and not state.get("in_position"):
            # Saldo abaixo do mínimo de ordem é resíduo (dust) e não deve bloquear novas entradas.
            try:
                price = float(client.get_symbol_ticker(symbol=SYMBOL)["price"])
                minimum = obter_minimo_notional(client, SYMBOL)
                balance_value = base_balance * price
                if minimum is not None and balance_value < minimum:
                    logging.info("Resíduo de %.8f %s (valor estimado %.4f; mínimo %.4f). "
                                 "Ignorando na reconciliação e liberando entradas.",
                                 base_balance, BASE_ASSET, balance_value, minimum)
                    state["external_position"] = False
                else:
                    # Não adota saldo negociável preexistente como posição do bot.
                    logging.error("Há %.8f %s (valor estimado %.4f) sem estado de posição. "
                                  "Entradas bloqueadas até reconciliar.",
                                  base_balance, BASE_ASSET, balance_value)
                    state["external_position"] = True
            except Exception:
                logging.exception("Não foi possível avaliar saldo preexistente de %s; mantendo bloqueio seguro.", BASE_ASSET)
                state["external_position"] = True
        elif base_balance > 0 and state.get("in_position"):
            state["external_position"] = False
            if state_quantity and abs(base_balance - state_quantity) > max(state_quantity * 0.05, 1e-8):
                logging.warning("Saldo livre (%.8f) difere da quantidade registrada (%.8f).", base_balance, state_quantity)
        salvar_estado(state)
    except Exception:
        logging.exception("Falha na reconciliação inicial; encerrando para evitar ordens com estado incerto.")
        return

    logging.info("Monitorando %s. Entrada aloca %.0f%% do saldo livre.", SYMBOL,
                 config.PERCENTUAL_SALDO_POR_ENTRADA * 100)

    while True:
        try:
            df = buscar_dados_historicos(client, SYMBOL, INTERVAL, CANDLE_COUNT)
            if df is None or df.empty:
                time.sleep(POLL_SECONDS)
                continue

            last_candle = df.iloc[-1]
            candle_id = last_candle["timestamp"].isoformat()
            current_price = float(last_candle["close"])
            in_position = bool(state.get("in_position"))

            # Stop e alvo são conferidos a cada ciclo, usando o preço atual do ticker.
            exit_reason = None
            entry_price = state.get("entry_price")
            if in_position and entry_price:
                current_price = float(client.get_symbol_ticker(symbol=SYMBOL)["price"])
                change = current_price / float(entry_price) - 1
                if change <= -config.STOP_LOSS_PERCENTUAL:
                    exit_reason = f"stop-loss ({change:.2%})"
                elif change >= config.TAKE_PROFIT_PERCENTUAL:
                    exit_reason = f"take-profit ({change:.2%})"

            is_new_candle = candle_id != state.get("last_candle")
            signal = analisar_mercado(df, config.RSI_COMPRA_MIN, config.RSI_COMPRA_MAX) if is_new_candle else "AGUARDAR"

            if in_position and (exit_reason or signal == "VENDER"):
                reason = exit_reason or "cruzamento EMA de baixa"
                quantity = calcular_quantidade(client, SYMBOL, BASE_ASSET, QUOTE_ASSET, percentual=0)
                order = executar_ordem(client, SYMBOL, SIDE_SELL, quantity)
                if order:
                    state.update(in_position=False, entry_price=None, quantity=0.0, external_position=False)
                    logging.info("Posição encerrada por %s. Ordem %s.", reason, order.get("orderId"))
                    enviar_email(f"VENDA EXECUTADA: {SYMBOL}", f"Motivo: {reason}\nOrdem: {order.get('orderId')}", True)
                    salvar_estado(state)
            elif not in_position and not state.get("external_position") and is_new_candle and signal == "COMPRAR":
                quantity = calcular_quantidade(client, SYMBOL, BASE_ASSET, QUOTE_ASSET,
                                               percentual=config.PERCENTUAL_SALDO_POR_ENTRADA)
                order = executar_ordem(client, SYMBOL, SIDE_BUY, quantity)
                if order:
                    fill_price = preco_medio_execucao(order)
                    if fill_price <= 0:
                        fill_price = float(client.get_symbol_ticker(symbol=SYMBOL)["price"])
                    executed_quantity = float(order.get("executedQty") or quantity)
                    state.update(in_position=True, entry_price=fill_price, quantity=executed_quantity,
                                 external_position=False)
                    logging.info("Compra executada. Quantidade %.8f, preço médio %.8f; stop %.2f%%, alvo %.2f%%.",
                                 executed_quantity, fill_price, config.STOP_LOSS_PERCENTUAL * 100,
                                 config.TAKE_PROFIT_PERCENTUAL * 100)
                    enviar_email(f"COMPRA EXECUTADA: {SYMBOL}",
                                 f"Quantidade: {executed_quantity}\nPreço médio: {fill_price}\nOrdem: {order.get('orderId')}", True)
                    salvar_estado(state)
            elif is_new_candle and signal == "COMPRAR" and state.get("external_position"):
                logging.warning("Sinal de compra ignorado: saldo preexistente precisa ser reconciliado.")

            if is_new_candle:
                state["last_candle"] = candle_id
                salvar_estado(state)
            time.sleep(POLL_SECONDS)
        except Exception as exc:
            logging.exception("Erro no loop principal")
            enviar_email("ERRO NO LOOP PRINCIPAL", f"Erro no loop principal: {exc}", False)
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
