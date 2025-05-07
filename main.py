import requests
import os
import time
import datetime
import logging
from telegram import Bot

# Token e username fixos (agora com o novo token e usuário)
TOKEN = "7643677472:AAGNI55sGVkPwxan6bPt00atR7nT1BRlhNk"
USER = "@victor_pinho87"
bot = Bot(token=TOKEN)

def send_telegram_message(message):
    try:
        bot.send_message(chat_id=USER, text=message)
    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem: {e}")

def fetch_trending_coins():
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        response = requests.get(url)
        data = response.json()
        coins = data.get("coins", [])
        return [coin["item"] for coin in coins]
    except:
        return []

def format_report(coins):
    top_3 = coins[:3]
    boas = [c for c in coins if c["market_cap_rank"] and c["market_cap_rank"] <= 100]
    shitcoins = [c for c in coins if c["market_cap_rank"] and c["market_cap_rank"] > 100]

    msg = f"📊 *Relatório Diário de Cripto – {datetime.datetime.now().strftime('%d/%m/%Y')}*\n\n"

    msg += "🔥 *3 moedas que estão bombando AGORA:*\n"
    for coin in top_3:
        msg += f"➡️ {coin['name']} ({coin['symbol'].upper()})\n"

    msg += "\n💎 *Moedas boas com volume alto:*\n"
    for coin in boas:
        msg += f"✅ {coin['name']} ({coin['symbol'].upper()})\n"

    msg += "\n💩 *Shitcoins com atenção alta:*\n"
    for coin in shitcoins:
        msg += f"⚠️ {coin['name']} ({coin['symbol'].upper()})\n"

    return msg

def run():
    coins = fetch_trending_coins()
    if not coins:
        send_telegram_message("⚠️ Não consegui buscar os dados de hoje.")
        return
    report = format_report(coins)
    send_telegram_message(report)

if __name__ == "__main__":
    print("🤖 Iniciando bot de alerta cripto")
    if os.getenv("FORCE_NOW") == "true":
        run()
    else:
        while True:
            now = datetime.datetime.now()
            if now.hour == 9 and now.minute == 0:
                run()
                time.sleep(60)
            time.sleep(10)
