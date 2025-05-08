import requests
import time
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import CommandHandler, CallbackContext, ApplicationBuilder

# Carregar variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Função /start
async def start(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Bot de alertas cripto ativo!")

# Função para buscar preço do Bitcoin
def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl"
    r = requests.get(url)
    data = r.json()
    return data["bitcoin"]["brl"]

# Histórico de preços para médias móveis
def get_bitcoin_history():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=brl&days=30"
    r = requests.get(url)
    data = r.json()
    prices = [p[1] for p in data["prices"]]
    return prices

# Análise fake de altcoins
def analisar_altcoins():
    altcoins = [
        {"nome": "dogecoin", "engajamento": 87},
        {"nome": "pepe", "engajamento": 91},
        {"nome": "shiba", "engajamento": 76}
    ]
    destaque = sorted(altcoins, key=lambda x: x["engajamento"], reverse=True)[:1]
    return destaque

# Verificar cruzamento de médias móveis
def verificar_cruzamento_mm(prices):
    if len(prices) < 25:
        return "Dados insuficientes para médias móveis"
    mm_curta = sum(prices[-7:]) / 7
    mm_longa = sum(prices[-25:]) / 25
    if mm_curta > mm_longa:
        return "🚀 Média móvel curta CRUZOU acima da longa – possível tendência de ALTA!"
    elif mm_curta < mm_longa:
        return "🔻 Média móvel curta CRUZOU abaixo da longa – possível tendência de BAIXA!"
    else:
        return "➖ Médias móveis estão se cruzando"

# Função principal de alerta
async def enviar_alerta(bot: Bot):
    try:
        preco = get_bitcoin_price()
        historico = get_bitcoin_history()
        cruzamento = verificar_cruzamento_mm(historico)
        altcoins = analisar_altcoins()

        mensagem = f"📈 *Alerta Cripto – {datetime.now().strftime('%d/%m %H:%M')}*\n"
        mensagem += f"💰 *Bitcoin*: R${preco:,.2f}\n"
        mensagem += f"{cruzamento}\n\n"
        mensagem += "🔥 Altcoin com maior engajamento:\n"
        for moeda in altcoins:
            mensagem += f"• {moeda['nome'].upper()} – Engajamento: {moeda['engajamento']}%\n"

        await bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Erro ao enviar alerta: {e}")

# Inicializar o bot com Application (v20+)
async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Comando /start
    application.add_handler(CommandHandler("start", start))

    # Agendador separado (APS)
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: application.bot.loop.create_task(enviar_alerta(application.bot)), 'interval', hours=4)
    scheduler.start()

    # Envia alerta imediato ao iniciar
    await enviar_alerta(application.bot)

    # Inicia polling
    print("✅ Bot iniciado. Escutando comandos e enviando alertas a cada 4 horas.")
    await application.run_polling()

# Executar
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
