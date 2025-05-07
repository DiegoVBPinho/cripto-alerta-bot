import requests
import os
import time
import datetime
from telegram import Bot

# Configurações do Bot
TOKEN = os.getenv("BOT_TOKEN", "7438251863:AAH9KEeqTTLMhaP_7XhDLAXs61SBwCXXaog")
USER = os.getenv("TELEGRAM_USER", "@victor_pinho87")
bot = Bot(token=TOKEN)

# Função para enviar mensagens para o Telegram
def send_telegram_message(message):
    try:
        bot.send_message(chat_id=USER, text=message, parse_mode="Markdown")
    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem: {e}")

# Buscar moedas em tendência
def fetch_trending_coins():
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        response = requests.get(url)
        data = response.json()
        coins = data.get("coins", [])
        return [coin["item"] for coin in coins]
    except Exception as e:
        print(f"[ERRO] Falha ao buscar moedas: {e}")
        return []

# Buscar métricas do Bitcoin
def fetch_bitcoin_price_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=10&interval=daily"
    try:
        response = requests.get(url)
        data = response.json()
        prices = [p[1] for p in data["prices"]]
        return prices[-7:]  # últimos 7 dias
    except Exception as e:
        print(f"[ERRO] Falha ao buscar dados do Bitcoin: {e}")
        return []

# Calcular médias móveis
def moving_average(prices, days):
    if len(prices) < days:
        return None
    return sum(prices[-days:]) / days

# Prever possível cruzamento
def check_moving_average_cross():
    prices = fetch_bitcoin_price_data()
    if len(prices) < 7:
        return None
    short_ma = moving_average(prices, 3)
    long_ma = moving_average(prices, 7)

    if not short_ma or not long_ma:
        return None

    if abs(short_ma - long_ma) / long_ma < 0.01:
        if short_ma > long_ma:
            return "🚀 *Curta acima da longa* - Possível sinal de *compra* de BTC."
        else:
            return "🔻 *Curta abaixo da longa* - Possível sinal de *venda* de BTC."
    return None

# Formatar relatório de moedas
def format_report(coins):
    top_3 = coins[:3]
    boas = [c for c in coins if c.get("market_cap_rank") and c["market_cap_rank"] <= 100]
    shitcoins = [c for c in coins if c.get("market_cap_rank") and c["market_cap_rank"] > 100]

    msg = f"\n📊 *Alerta Cripto* – {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n"

    msg += "\n🔥 *Top 3 moedas do momento:*"
    for coin in top_3:
        msg += f"➡️ {coin['name']} ({coin['symbol'].upper()})\n"

    if boas:
        msg += "\n💎 *Moedas boas com volume alto:*"
        for coin in boas:
            msg += f"✅ {coin['name']} ({coin['symbol'].upper()})\n"

    if shitcoins:
        msg += "\n💩 *Shitcoins em alta atenção:*"
        for coin in shitcoins:
            msg += f"⚠️ {coin['name']} ({coin['symbol'].upper()})\n"

    return msg

# Loop principal
def run():
    coins = fetch_trending_coins()
    aviso_ma = check_moving_average_cross()

    if not coins:
        send_telegram_message("⚠️ Falha ao buscar dados do CoinGecko.")
        return

    report = format_report(coins)
    if aviso_ma:
        report += "\n\n📈 *Análise BTC:*\n" + aviso_ma

    send_telegram_message(report)

if __name__ == "__main__":
    print("🤖 Bot iniciado...")
    while True:
        run()
        time.sleep(4 * 60 * 60)  # Executa a cada 4 horas
