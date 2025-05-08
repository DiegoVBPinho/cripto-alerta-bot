import requests
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Agora você pode acessar a chave de API e o chat_id de maneira segura
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telegram.Bot(token=TOKEN)

# Função start do bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("✅ Bot de alertas cripto ativo!")

# Função para buscar preço do Bitcoin
def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=brl"
    r = requests.get(url)
    data = r.json()
    return data["bitcoin"]["brl"]

# Função para buscar histórico de preços (para calcular médias)
def get_bitcoin_history():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=brl&days=30"
    r = requests.get(url)
    data = r.json()
    prices = [p[1] for p in data["prices"]]
    return prices

# Simulação de análise de altcoins com "potencial de pump"
def analisar_altcoins():
    altcoins = [
        {"nome": "dogecoin", "engajamento": 87},
        {"nome": "pepe", "engajamento": 91},
        {"nome": "shiba", "engajamento": 76}
    ]
    destaque = sorted(altcoins, key=lambda x: x["engajamento"], reverse=True)[:1]
    return destaque

# Cruzamento de médias móveis (simples de 7 e 25 dias)
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

# Mensagem principal do bot
async def enviar_alerta():
    try:
        preco = get_bitcoin_price()
        historico = get_bitcoin_history()
        cruzamento = verificar_cruzamento_mm(historico)
        altcoins = analisar_altcoins()

        mensagem = f"📈 *Alerta Cripto – {datetime.now().strftime('%d/%m %H:%M')}*"

        mensagem += f"💰 *Bitcoin*: R${preco:,.2f}"
        mensagem += f"{cruzamento}"
        mensagem += "🔥 Altcoin com maior engajamento:"
        for moeda in altcoins:
            mensagem += f"• {moeda['nome'].upper()} – Engajamento: {moeda['engajamento']}%"

        await bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode=telegram.ParseMode.MARKDOWN)
    except Exception as e:
        logging.error(f"Erro ao enviar alerta: {e}")

# Agendador
scheduler = BlockingScheduler()
scheduler.add_job(enviar_alerta, 'interval', hours=4)
print("✅ Bot iniciado. Enviando alertas a cada 4 horas.")
enviar_alerta()  # Envia um alerta logo ao iniciar
scheduler.start()

# Iniciando o bot
application = Application.builder().token(TOKEN).build()

application.add_handler(CommandHandler("start", start))

application.run_polling()
