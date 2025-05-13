import telebot
import threading
import time
from datetime import datetime

# Token do seu bot
bot = telebot.TeleBot('7438251863:AAH9KEeqTTLMhaP_7XhDLAXs61SBwCXXaog')

# Seu chat ID
chat_id_do_destino = 877947244

# Comando básico de início
@bot.message_handler(commands=['start'])
def start(msg: telebot.types.Message):
    bot.reply_to(msg, 'Bot de cripto ligado! Vou te mandar alertas a cada 4 horas. 🔔')

# Função que envia alertas de cripto
def enviar_alertas_automaticamente():
    while True:
        try:
            agora = datetime.now().strftime('%d/%m %H:%M')
            texto = (
                f'🚨 Alerta de Cripto - {agora}\n'
                f'- BTC: R$ 345.000\n'
                f'- ETH: R$ 18.200\n'
                f'- TOP 3 moedas com potencial de pump:\n'
                f'1. PEPE 🚀\n2. FLOKI 🐶\n3. BONK 🔥\n\n'
                f'Volume social alto e engajamento positivo!'
            )
            bot.send_message(chat_id_do_destino, texto)
            print(f'[OK] Alerta enviado: {agora}')
        except Exception as e:
            print(f"[ERRO] Falha ao enviar alerta: {e}")
        
        time.sleep(4 * 60 * 60)  # Espera 4 horas

# Inicia os alertas em thread separada
threading.Thread(target=enviar_alertas_automaticamente, daemon=True).start()

# Mantém o bot rodando e ouvindo comandos
bot.infinity_polling()
