import logging
from decimal import Decimal, ROUND_DOWN

from binance.enums import ORDER_TYPE_MARKET, SIDE_BUY
from binance.exceptions import BinanceAPIException

from core.notifier import enviar_email


def obter_saldo(client, ativo):
    try:
        for balance in client.get_account()["balances"]:
            if balance["asset"] == ativo:
                return float(balance["free"])
        return 0.0
    except Exception:
        logging.exception("Erro ao buscar saldo de %s", ativo)
        return 0.0


def _filtros(client, symbol):
    info = client.get_symbol_info(symbol)
    if not info:
        raise ValueError(f"Símbolo não encontrado: {symbol}")
    return {item["filterType"]: item for item in info["filters"]}


def obter_minimo_notional(client, symbol):
    """Retorna o valor mínimo negociável do par, ou None se não estiver disponível."""
    try:
        filters = _filtros(client, symbol)
        for filter_type in ("NOTIONAL", "MIN_NOTIONAL"):
            minimum = filters.get(filter_type, {}).get("minNotional")
            if minimum is not None:
                return float(minimum)
    except Exception:
        logging.exception("Erro ao consultar valor mínimo para %s", symbol)
    return None


def calcular_quantidade(client, symbol, ativo_base, ativo_cotacao, percentual=0.95):
    """Calcula quantidade respeitando stepSize e validações de lote/valor mínimo."""
    try:
        filters = _filtros(client, symbol)
        # A ordem é MARKET; quando disponível, valide o filtro específico dela.
        lot = filters.get("MARKET_LOT_SIZE") or filters.get("LOT_SIZE")
        if not lot:
            raise ValueError("Filtro de lote ausente")
        step = Decimal(lot["stepSize"])

        if percentual > 0:
            if not 0 < percentual <= 1:
                raise ValueError("percentual deve estar entre 0 e 1")
            quote_balance = Decimal(str(obter_saldo(client, ativo_cotacao)))
            price = Decimal(str(client.get_symbol_ticker(symbol=symbol)["price"]))
            raw = quote_balance * Decimal(str(percentual)) / price
        else:
            raw = Decimal(str(obter_saldo(client, ativo_base)))

        quantity = (raw / step).to_integral_value(rounding=ROUND_DOWN) * step
        if quantity < Decimal(lot["minQty"]) or quantity > Decimal(lot["maxQty"]):
            logging.warning("Quantidade %s fora dos limites LOT_SIZE do par %s", quantity, symbol)
            return 0.0

        price = Decimal(str(client.get_symbol_ticker(symbol=symbol)["price"]))
        min_notional = filters.get("NOTIONAL", filters.get("MIN_NOTIONAL", {})).get("minNotional")
        if min_notional and quantity * price < Decimal(min_notional):
            logging.warning("Valor estimado %.8f abaixo do mínimo de %s para %s", quantity * price, min_notional, symbol)
            return 0.0
        return float(quantity)
    except Exception:
        logging.exception("Erro ao calcular quantidade para %s", symbol)
        return 0.0


def preco_medio_execucao(order):
    fills = order.get("fills") or []
    total_qty = sum(Decimal(fill["qty"]) for fill in fills)
    total_quote = sum(Decimal(fill["qty"]) * Decimal(fill["price"]) for fill in fills)
    if total_qty:
        return float(total_quote / total_qty)
    executed = Decimal(str(order.get("executedQty", "0")))
    quote = Decimal(str(order.get("cummulativeQuoteQty", "0")))
    return float(quote / executed) if executed else 0.0


def executar_ordem(client, symbol, side, quantity):
    try:
        if quantity <= 0:
            logging.warning("Quantidade zero; ordem cancelada.")
            return None
        direction = "COMPRA" if side == SIDE_BUY else "VENDA"
        logging.info("Enviando ordem a mercado: %s %s %s", direction, quantity, symbol)
        order = client.create_order(symbol=symbol, side=side, type=ORDER_TYPE_MARKET, quantity=quantity)
        logging.info("Ordem executada; id=%s", order.get("orderId"))
        return order
    except BinanceAPIException as exc:
        logging.error("Erro da Binance: %s - %s", exc.status_code, exc.message)
        enviar_email("ERRO NA ORDEM", f"Erro da Binance: {exc.status_code} - {exc.message}", False)
        return None
    except Exception as exc:
        logging.exception("Erro inesperado ao enviar ordem")
        enviar_email("ERRO NA ORDEM", f"Erro inesperado ao enviar ordem: {exc}", False)
        return None
