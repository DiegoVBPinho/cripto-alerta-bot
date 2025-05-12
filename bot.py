import requests
import logging
import os
from dotenv import load_dotenv
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

# Token e Chat ID
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telegram.Bot(token=TOKEN)

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Comando /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("✅ Bot de alertas cripto ativo!")

# Buscar preço do Bitcoin
def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl"
    r = requests.get(url)
    data = r.json()
    return data["bitcoin"]["brl"]

# Buscar histórico de preços do Bitcoin
def get_bitcoin_history():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=brl&days=30"
    r = requests.get(url)
    data = r.json()
    prices = [p[1] for p in data["prices"]]
    return prices

# Simular análise de altcoins
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

# Enviar alerta
async def enviar_alerta():
    try:
        preco = get_bitcoin_price()
        historico = get_bitcoin_history()
        cruzamento = verificar_cruzamento_mm(historico)
        altcoins = analisar_altcoins()

        mensagem = f"📈 *Alerta Cripto – {datetime.now().strftime('%d/%m %H:%M')}*"
        mensagem += f"\n💰 *Bitcoin*: R${preco:,.2f}"
        mensagem += f"\n{cruzamento}"
        mensagem += "\n🔥 Altcoin com maior engajamento:"
        for moeda in altcoins:
            mensagem += f"\n• {moeda['nome'].upper()} – Engajamento: {moeda['engajamento']}%"

        await bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode=telegram.ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Erro ao enviar alerta: {e}")

# Agendar alertas
async def agendar_alertas():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(enviar_alerta, 'interval', hours=4)
    scheduler.start()

# Função principal com loop correto para Railway
async def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    await application.initialize()
    await application.start()
    await agendar_alertas()
    await application.updater.start_polling()
    await application.updater.idle()

# Rodar app
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
