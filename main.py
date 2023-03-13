
import telebot
import requests

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'} 

from bs4 import BeautifulSoup
  
def get_ticker_value(ticker):
    url = f'https://www.google.com/search?q={ticker}'
    res = requests.get(url, headers=headers)
    html_page = res.text

    
    soup = BeautifulSoup(html_page, 'html.parser')

    #print(soup.find_all('span'))

    valor = float(soup.find_all('span', {"class":'IsqQVc NprOob wT3VGc'})[0].text.replace(",","."))
    return valor

bot = telebot.TeleBot("5747986812:AAG7f__d2EsGA-OcjV3_dquK7pA7KIqb-so")

comandos = [
    ("start", "Iniciar"),
    ("cotacao", "Mostra a cotação de um fundo imobiliário. Ex.: /cotacao ARCT11"),
    ] 
    

@bot.message_handler(regexp=r"(\s)*/cotacao.* [A-Za-z]{4}11")
def handle_command(message):
    try:
        print(message.from_user.first_name, message.text)
        ticker = message.text.split()[1].strip()
        enviada = bot.send_message(message.chat.id, "Buscando...", reply_to_message_id=message.id)
        valor = get_ticker_value(ticker)
        bot.delete_message(message.chat.id, enviada.id)
        bot.send_message(message.chat.id, f"R$ {valor:.2f}".replace(".",","), reply_to_message_id=message.id)
    except:
        bot.send_message(message.chat.id, 'Ocorreu um erro, tente novamente.')

@bot.message_handler(commands=["start"])
def handle_command(message):
    print(message)
    bot.send_message(message.from_user.id, "Pronto", reply_to_message_id=message.id)  
    
bot.set_my_commands([telebot.types.BotCommand(comando[0], comando[1]) for comando in comandos])

print("Robô iniciado.")
bot.infinity_polling()