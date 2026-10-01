# CryptoTradingBot

Bot modular de negociação algorítmica em Python, integrado à API da Binance. Ele monitora o par `ZECUSDT` em candles de 15 minutos, calcula sinais com EMA e RSI e envia ordens a mercado. O projeto também oferece notificações por e-mail e salva o estado da posição em `bot_state.json`.

> **Atenção:** a configuração atual usa a API de negociação **real** (`USE_DEM0 = False`) e pode enviar ordens com dinheiro real. Revise `config.py` e teste cuidadosamente antes de executar. Negociação de criptoativos pode causar perdas.

## Funcionalidades

- Cruzamento de EMA 9 e EMA 21, com RSI 14 para confirmar entradas.
- Compra usando 95% do saldo livre de USDT; quantidade ajustada aos filtros de lote e valor mínimo da Binance.
- Saída por cruzamento de baixa, stop-loss de 2% ou take-profit de 4%.
- Reconciliação inicial do saldo com o estado local para evitar entradas quando há uma posição preexistente sem correspondência.
- Consulta de candles fechados e verificação de preço a cada 60 segundos.
- Alertas HTML por e-mail para execuções e erros.

Os parâmetros de risco, RSI e ambiente estão em `config.py`. O mercado, intervalo e frequência de consulta estão definidos no início de `main.py`.

## Estrutura

```text
core/connection.py     Conexão e autenticação na Binance
core/notifier.py       Envio de alertas por e-mail
data/market.py         Consulta e preparação de candles
execution/orders.py   Saldo, filtros, quantidade e ordens a mercado
strategies/rsi_ema.py  Sinais de EMA e RSI
templates/             Modelo HTML do e-mail
config.py              Credenciais e parâmetros da estratégia
main.py                Loop principal e persistência do estado
bot_state.json         Estado local da posição (criado/atualizado em execução)
```

## Requisitos

- Python 3.12 (a imagem Docker usa `python:3.12-slim`)
- Uma conta Binance e uma chave de API com permissões adequadas ao ambiente selecionado
- Docker, opcionalmente

## Instalação local

```bash
git clone https://github.com/gsiilva/CryptoTradingBot.git
cd CryptoTradingBot
python -m venv .venv
```

Ative o ambiente virtual e instale as dependências:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS (use este comando em vez do comando do Windows)
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuração

O programa lê as credenciais das variáveis de ambiente. Defina estas quatro variáveis antes de iniciar:

| Variável | Uso |
|---|---|
| `BINANCE_API_KEY_REAL` | Chave da API Binance |
| `BINANCE_API_SECRET_REAL` | Segredo da API Binance |
| `BOT_EMAIL_ADRESS` | Conta Gmail remetente (o nome da variável usa essa grafia no código) |
| `BOT_16_PASSWORD` | Senha de app do Gmail |
| `PERSONAL_EMAIL` | Endereço destinatário dos alertas |

Exemplo no PowerShell (válido para a sessão atual):

```powershell
$env:BINANCE_API_KEY_REAL = "sua_chave"
$env:BINANCE_API_SECRET_REAL = "seu_segredo"
$env:BOT_EMAIL_ADRESS = "remetente@gmail.com"
$env:BOT_16_PASSWORD = "senha_de_app"
$env:PERSONAL_EMAIL = "destinatario@example.com"
```

Não compartilhe nem versione suas credenciais. Para usar o ambiente Demo, ajuste `USE_DEM0` em `config.py` e use credenciais correspondentes ao ambiente Demo. O valor padrão no código é `False` (Real).

## Execução

```bash
python main.py
```

O processo permanece em execução e registra eventos no console. Interrompa-o com `Ctrl+C`. `bot_state.json` é usado para retomar o acompanhamento da posição após reinicializações; mantenha esse arquivo persistente e não o edite enquanto o bot estiver rodando.

## Docker

Construa a imagem e execute o container passando as mesmas variáveis de ambiente:

```bash
docker build -t crypto-trading-bot .
docker run --env-file .env -v "${PWD}/bot_state.json:/app/bot_state.json" crypto-trading-bot
```

Crie `.env` localmente com as variáveis listadas acima (uma por linha). O arquivo `.env` está no `.gitignore`; não o adicione ao controle de versão. O volume mantém o estado local entre execuções. Para operação contínua, configure a política de reinício do container conforme seu ambiente.

## Estratégia e gestão de posição

Uma compra é considerada quando a EMA 9 cruza acima da EMA 21 e o RSI está entre os limites configurados (40–65 por padrão) e subindo. A venda ocorre no cruzamento de baixa ou quando o preço atinge o stop ou o alvo definidos. Os sinais são avaliados em candles fechados; stop-loss e take-profit usam o preço atual consultado durante cada ciclo.

## Aviso

Este software é fornecido para fins educacionais e de teste, sem garantia de resultados. Verifique a configuração, as permissões da chave e as ordens antes de usar. O usuário é responsável pelas decisões e perdas associadas à negociação.
