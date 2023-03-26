import pandas as pd

import requests
import telebot
#import pandas as pd
import time
import urllib
from threading import Thread
import re

from telethon import TelegramClient
import asyncio
from telethon.tl.types import DocumentAttributeVideo, InputMediaUploadedDocument

import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import datetime

import xmltodict

client = gspread.service_account(filename='superfiisbot-9f67df851d9a.json')

sheet = client.open("Teste").sheet1

telebot.apihelper.SESSION_TIME_TO_LIVE = 60 * 15


bot = telebot.TeleBot("5747986812:AAG7f__d2EsGA-OcjV3_dquK7pA7KIqb-so")

comandos = [
    ("start", "Iniciar"),
    ("cotacao", "Mostra a cotação de um fundo imobiliário. Ex.: /cotacao URPR11"),
    ("seguir", "Use para receber todos os documentos e informações de rendimentos de um FII. Ex.: /seguir URPR11"),
    ("desinscrever", "Use para deixar de um FII que você segue. Ex.: /desinscrever URPR11"),
    ("fundos_seguidos", "Lista todos os fundos imobiliários que você segue."),
    ("ultimos_documentos", "Receba os documentos emitidos pelo fundos nos últimos 30 dias. Ex.: /ultimos_documentos URPR11"),
    ("teste", "Teste"),
    ]

fiis_cnpj = pd.read_csv("fiis_cnpj.csv", dtype={"Código":str, "CNPJ":str}).dropna()

bot = telebot.TeleBot("5747986812:AAG7f__d2EsGA-OcjV3_dquK7pA7KIqb-so")    

class BaseCache:
    def __init__(self, base): #planilha do tipo dict
        self.base_dados = base
        planilha_lista = base.get_all_values()
        self.planilha = {}
        self.indices = {}
        self.celulas_vazias = {}
        for i, f in enumerate(planilha_lista[0]):
            self.planilha[f] = []
            self.indices[f] = i+1
        for i in range(0, len(planilha_lista[0])):
            for j in range(1, len(planilha_lista)):
                self.planilha[planilha_lista[0][i]].append(str(planilha_lista[j][i]))
        for k in self.planilha.keys():
            self.celulas_vazias[k] = []
            for j, cel in enumerate(self.planilha[k]):
                if cel == "":
                    self.celulas_vazias[k].append((j+2,self.indices[k]))
        #print(self.planilha)
        #print(self.celulas_vazias)
        
    def inserir(self, coluna, valor):
        if coluna not in self.planilha:
            return -1
        elif valor in self.planilha[coluna]:
            return 1
        self.planilha[coluna].append(valor)
        self.atualizar_celula(coluna, len(self.planilha[coluna])-1)
        return 0
        
    def remover(self, coluna, valor):
        if coluna not in self.planilha:
            return -1
        elif valor not in self.planilha[coluna]:
            return 1
        indice = self.planilha[coluna].index(valor)
        self.planilha[coluna][indice] = ""
        self.atualizar_celula(coluna, indice)
        return 0
        
    def atualizar_celula(self, coluna, indice):
        self.base_dados.update_cell(indice+2, self.indices[coluna], self.planilha[coluna][indice])
        
    def buscar_seguidos(self, usuario):
        seguidos = []
        for f in sorted(self.planilha.keys()):
            if usuario in self.planilha[f]:
                seguidos.append(f)
        return seguidos

base = BaseCache(sheet)

def informar_proventos(doc, usuario):
#422748
    r = requests.get(f'https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id={doc["id"]}', headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"})

    dados = xmltodict.parse(r.content)

    mensagem = "Informação de proventos:"
    #mensagem += f'FII: {doc["codigoFII"]}'

    for d in dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]:
        if type(d) == str:
            #print(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["CodNegociacao"])
            if d == "CodNegociacao":
                print(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["CodNegociacao"])
                #mensagem += f'\n\nCódigo: {dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["CodNegociacao"]}'
            elif d == "Rendimento":
                mensagem += f'\n\n\U0001F3E0Código: {dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["CodNegociacao"]}'
                print(float(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["ValorProvento"]))
                mensagem += f'\n\U0001F4B0Rendimento: R$ {conv_monet(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["ValorProvento"])}'
                mensagem += f'\n\U0001F5D3Data base: {conv_data(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["DataBase"])}'
                mensagem += f'\n\U0001F4B8Data de pagamento: {conv_data(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["DataPagamento"])}'
            elif d == "Amortizacao":
                mensagem += f'\n\n\U0001F3E0Código: {dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["CodNegociacao"]}'
                print(float(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Amortizacao"]["ValorProvento"]))
                mensagem += f'\n\U0001F4B0Amortização: R$ {conv_monet(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Amortizacao"]["ValorProvento"])}'
                mensagem += f'\n\U0001F5D3Data base: {conv_data(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["DataBase"])}'
                mensagem += f'\n\U0001F4B8Data de pagamento: {conv_data(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["DataPagamento"])}'
        else:
            print(d["CodNegociacao"])
            
            for d2 in d:
                if d2 == "Rendimento":
                    mensagem += f'\n\n\U0001F3E0Código: {d["CodNegociacao"]}'
                    print(float(d[d2]["ValorProvento"]))
                    mensagem += f'\n\U0001F4B0Rendimento: R$ {conv_monet(d[d2]["ValorProvento"])}'
                    mensagem += f'\n\U0001F5D3Data base: {conv_data(d[d2]["DataBase"])}'
                    mensagem += f'\n\U0001F4B8Data de pagamento: {conv_data(d[d2]["DataPagamento"])}'
                elif d2 == "Amortizacao":
                    mensagem += f'\n\n\U0001F3E0Código: {d["CodNegociacao"]}'
                    print(d[d2]["ValorProvento"])
                    mensagem += f'\n\U0001F4B0Amortização: R$ {conv_monet(d[d2]["ValorProvento"])}'
                    mensagem += f'\n\U0001F5D3Data base: {conv_data(d[d2]["DataBase"])}'
                    mensagem += f'\n\U0001F4B8Data de pagamento: {conv_data(d[d2]["DataPagamento"])}'
        #print(mensagem)
        
    mensagem += "\n\n@SuperFIIsBot"
    bot.send_message(usuario, mensagem)
        
def conv_data(data):
    return f"{data[8:10]}/{data[5:7]}/{data[0:4]}"
    
def conv_monet(valor):
    try:
        virgula = valor.index(".")
        if virgula < len(valor)-2:
            while valor[-1] == "0":
                valor = valor[:-1]
        if virgula == len(valor)-2:
            valor += "0"
        elif virgula == len(valor)-1:
            valor += "00"
    except:
        valor += ",00"
    return valor.replace(".", ",")
    
def buscar_documentos(cnpj, desde=""):
    #cnpj 11179118000145
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=1&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}")
    lista = []
    for d in r.json()["data"]:
        de = d["dataEntrega"]
        print(datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13])), desde)
        if datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13]), minute=int(de[14:16])) < desde:
            break
        if d["status"] == "AC":
            lista.append(d)
    lista.reverse()
    return lista
    
def buscar_documentos2(cnpj, desde=""):
    #cnpj 11179118000145
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=1&s=0&l=30&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}")
    lista = []
    for d in r.json()["data"]:
        de = d["dataEntrega"]
        print(datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13])), desde)
        if datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13]), minute=int(de[14:16])) < desde:
            break
        if d["status"] == "AC":
            lista.append(d)
    lista.reverse()
    return lista
        
def baixarDocumento(link):
    pass
  
  
def env(doc, usuario):
        if doc["categoriaDocumento"] in ("Informes Periódicos", "Aviso aos Cotistas - Estruturado") and doc["tipoDocumento"] != "Demonstrações Financeiras" or "Estruturado" in doc["tipoDocumento"]:
            data_ref = re.search(r"\d\d/\d\d\d\d", doc["dataReferencia"])
            data_ref = "("+data_ref.group()+")" if data_ref else doc["dataReferencia"].replace("/", "-").replace(":", "-")
            bot.send_document(
            usuario,
            xml_pdf(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}'),
            visible_file_name="Arquivo.pdf",
            caption=f'{doc["codigoFII"]} - {doc["tipoDocumento"]} {data_ref}\n\n@SuperFIIsBot'
            )
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tipo_doc = doc["tipoDocumento"].replace("/", "-") if doc["tipoDocumento"].strip() != "" else doc["categoriaDocumento"]
            with TelegramClient("bot", "14595347", "ff2597a5880da0bdd36363b2c8a3aa94").start(bot_token="5747986812:AAG7f__d2EsGA-OcjV3_dquK7pA7KIqb-so") as client:
             with open(f'{tipo_doc}.pdf', "wb") as f:
                f.write(requests.get(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}', headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"}).content)
                loop.run_until_complete(asyncio.wait([ enviar_documento( doc, usuario, client)]))
             os.remove(f'{tipo_doc}.pdf')
           
   
async def enviar_documento(doc, usuario, client):
    #doc_id 430265
    tipo_doc = doc["tipoDocumento"].replace("/", "-") if doc["tipoDocumento"].strip() != "" else doc["categoriaDocumento"]
    if tipo_doc == "Relatório Gerencial":
        data_ref = re.search(r"\d\d/\d\d\d\d", doc["dataReferencia"])
    else:
        data_ref = re.search(r"\d\d/\d\d/\d\d\d\d", doc["dataReferencia"])
    data_ref = "("+data_ref.group()+")" if data_ref else doc["dataReferencia"].replace("/", "-").replace(":", "-")
    if False:#doc["categoriaDocumento"] in ("Informes Periódicos",):
        bot.send_document(
        usuario,
        xml_pdf(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}'),
        visible_file_name="Arquivo.pdf",
        caption=f'{doc["tipoDocumento"]} {doc["dataReferencia"][-7:].replace("/","-")} - {doc["descricaoFundo"]}'
        )
    else:
        #remote_url = f'https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id={r.json()["data"][1]["id"]}'
# Define the local filename to save data
#local_file = f'{r.json()["data"][1]["tipoDocumento"]} {r.json()["data"][1]["dataReferencia"][-7:].replace("/","-")} - {r.json()["data"][1]["descricaoFundo"]}.pdf'

        #with open("Documento.pdf", "wb") as f:
            #f.write(requests.get(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}', headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"}).content)
            
        #fu = urllib.request.Request(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}', headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"})
        #fff = urllib.request.urlopen(fu)
            
        #time.sleep(2)
        #with open("/home/gilmartaj/SuperFIIs/Documento.pdf", "rb") as ff:
        
            #files = {"document": ff}
            #values = {"chat_id": usuario}
            #requests.post("http://api.telegram.org/bot5747986812:AAG7f__d2EsGA-OcjV3_dquK7pA7KIqb-so/sendDocument", files=files, data=values)
            
            #bot.send_document(556068392,open("/home/gilmartaj/SuperFIIs/Documento.pdf", "rb"), timeout=200)
            with open(f'{tipo_doc}.pdf', "rb") as fp:
                    await client.send_file(usuario, file=fp, caption=f'{doc["codigoFII"]} - {tipo_doc} {data_ref}\n\n@SuperFIIsBot')
    
def buscar_cnpj(codigo_fii):
    return fiis_cnpj.where(fiis_cnpj["Código"] == codigo_fii).dropna().iloc[0]["CNPJ"]


def xml_pdf(link):
    h = {

    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIiLCJhdWQiOiIiLCJpYXQiOjE1MjMzNjQ4MjQsIm5iZiI6MTUyMzM2NDgyNCwianRpIjoicHJvamVjdF9wdWJsaWNfYzkwNWRkMWMwMWU5ZmQ3NzY5ODNjYTQwZDBhOWQyZjNfT1Vzd2EwODA0MGI4ZDJjN2NhM2NjZGE2MGQ2MTBhMmRkY2U3NyJ9.qvHSXgCJgqpC4gd6-paUlDLFmg0o2DsOvb1EUYPYx_E',
    'Content-Type': 'multipart/form-data; boundary=---------------------------23846124012560570869635858195',
    'Origin': 'https://www.ilovepdf.com',
    'Connection': 'keep-alive'
    }


    h2 = {

    'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiIiLCJhdWQiOiIiLCJpYXQiOjE1MjMzNjQ4MjQsIm5iZiI6MTUyMzM2NDgyNCwianRpIjoicHJvamVjdF9wdWJsaWNfYzkwNWRkMWMwMWU5ZmQ3NzY5ODNjYTQwZDBhOWQyZjNfT1Vzd2EwODA0MGI4ZDJjN2NhM2NjZGE2MGQ2MTBhMmRkY2U3NyJ9.qvHSXgCJgqpC4gd6-paUlDLFmg0o2DsOvb1EUYPYx_E',
    'Content-Type': 'multipart/form-data; boundary=---------------------------60486432820756574052288473281',
    'Origin': 'https://www.ilovepdf.com',
    'Connection': 'keep-alive'
    }

    h3 = {}

    server_file = requests.post(f"https://api32.ilovepdf.com/v1/upload", headers=h, data=f'-----------------------------23846124012560570869635858195\r\nContent-Disposition: form-data; name="task"\r\n\r\nw3xjsv3pgkt1hklngy36z0v2q0pdhv01rpx7brwwyxd7AAztccm2p3g9nkwq6gbc2085df55v058qyx32lsktAg8mvtmxlxm1zj3h1h20gvtkgdmr6dy5mnlkkntqgAdk7ssy1z9yq00bjm42rfzlv6qpw4b1yp48Av3mggqA60rg7p7zygq\r\n-----------------------------23846124012560570869635858195\r\nContent-Disposition: form-data; name="cloud_file"\r\n\r\n{link}\r\n-----------------------------23846124012560570869635858195--\r\n'.encode("utf-8")).json()["server_filename"]

    print(server_file)

    #sys.exit(0)

    preview = requests.post(f"https://api32.ilovepdf.com/v1/preview", headers=h2, data=f'-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="server_filename"\r\n\r\n{server_file}\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="task"\r\n\r\nw3xjsv3pgkt1hklngy36z0v2q0pdhv01rpx7brwwyxd7AAztccm2p3g9nkwq6gbc2085df55v058qyx32lsktAg8mvtmxlxm1zj3h1h20gvtkgdmr6dy5mnlkkntqgAdk7ssy1z9yq00bjm42rfzlv6qpw4b1yp48Av3mggqA60rg7p7zygq\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="page_orientation"\r\n\r\nportrait\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="page_margin"\r\n\r\n0\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="url"\r\n\r\nhttps://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=430731&cvm=true&#toolbar=0\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="view_width"\r\n\r\n768\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="page_size"\r\n\r\nA4\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="single_page"\r\n\r\ntrue\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="block_ads"\r\n\r\nfalse\r\n-----server------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="remove_popups"\r\n\r\nfalse\r\n-----------------------------60486432820756574052288473281--\r\n'.encode("utf-8")).json()["thumbnail"]

    return f'https://api32.ilovepdf.com/thumbnails/{preview}'


"""r = requests.get("https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=1&s=0&l=2&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo=11179118000145")

bot = telebot.TeleBot("5747986812:AAG7f__d2EsGA-OcjV3_dquK7pA7KIqb-so")

print(r.json()["data"][1]["dataEntrega"])


remote_url = f'https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id={r.json()["data"][1]["id"]}'
# Define the local filename to save data
local_file = f'{r.json()["data"][1]["tipoDocumento"]} {r.json()["data"][1]["dataReferencia"][-7:].replace("/","-")} - {r.json()["data"][1]["descricaoFundo"]}.pdf'

open(local_file, "wb").write(requests.get(remote_url, headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"}).content)
"""

@bot.message_handler(commands=["teste"])
def handle_command(message):
    print(message)
    #with open('/home/gilmartaj/SuperFIIs/Relatório Gerencial 02-2023 - FII ANHANGUERA EDUCACIONAL.pdf', 'rb') as f:
    """bot.send_document(
    message.from_user.id,
    'https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id=430265',
    visible_file_name="Relatório.pdf",
    caption="2023"
    )"""
    
    print("\n\n\nbbbb\n\n\n")
    for fii in ("MCHF11", "HCTR11", "APTO11", "CYCR11", "FAED11", "HGIC11", "MCHF11", "RZAT11", "URPR11", "VGHF11","KIVO11", "LIFE11", "MCHY11", "MFCR11", "MGHT11", "PLOG11", "RPRI11", "KINP11"):
        aaa = buscar_documentos2(buscar_cnpj(fii), datetime.datetime.now()-datetime.timedelta(days=60))
        
        
        for a in aaa:
            print(fii, "-", a["tipoDocumento"])
            
            a["codigoFII"] = fii
            #Thread(target=enviar_documento, args=(a, message.from_user.id), daemon=True).start()
            #bot.set_my_commands([telebot.types.BotCommand(comando[0], comando[1]) for comando in comandos])"""
            env(a, message.from_user.id)
            if a["tipoDocumento"] == "Rendimentos e Amortizações":
                informar_proventos(a, message.from_user.id)
            
            
@bot.message_handler(commands=["ultimos_documentos"])
def handle_command(message):

    print(message)

    ticker = message.text.split()[1].strip().upper()
    documentos = buscar_documentos2(buscar_cnpj(ticker), datetime.datetime.now() - datetime.timedelta(days=30))
    print(documentos)
        
    for a in documentos:
        print(ticker, "-", a["tipoDocumento"])
        a["codigoFII"] = ticker
        env(a, message.from_user.id)

@bot.message_handler(commands=["seguir"])
def handle_command(message):
    print(message)
    ticker = message.text.split()[1].strip().upper()
    r = base.inserir(ticker, str(message.from_user.id))
    if r == 0:
        bot.send_message(message.chat.id, f"Parabéns! Agora você receberá todos os documentos e comunicados referentes ao fundo {ticker}.", reply_to_message_id=message.id)
    elif r == 1:
        bot.send_message(message.chat.id, "Você já segue esse fundo. Assim que forem divulgados novos documentos ou comunicados, lhe enviaremos.", reply_to_message_id=message.id)
    elif r == -1:
        bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo imobiliário {ticker}.", reply_to_message_id=message.id)
        
@bot.message_handler(commands=["desinscrever"])
def handle_command(message):
    print(message)
    ticker = message.text.split()[1].strip().upper()
    r = base.remover(ticker, str(message.from_user.id))
    if r == 0:
        bot.send_message(message.chat.id, f"Pronto! Você não receberá mais informações sobre o fundo {ticker}.", reply_to_message_id=message.id)
    elif r == 1:
        bot.send_message(message.chat.id, f'Você ainda não segue esse fundo. Para seguir envie: "/seguir {ticker}"', reply_to_message_id=message.id)
    elif r == -1:
        bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo imobiliário {ticker}.", reply_to_message_id=message.id)
        
@bot.message_handler(commands=["fundos_seguidos"])
def handle_command(message):
    print(message)
    fs = base.buscar_seguidos(str(message.from_user.id))
    if len(fs) == 0:
        bot.send_message(message.chat.id, f"Você ainda não está seguindo nenhum fundo imobiliário. Para começar, utilize o comando /seguir", reply_to_message_id=message.id)
    else:
        resposta = "FIIs que você segue:"
        for f in fs:
            resposta += "\n"+f
        bot.send_message(message.chat.id, resposta, reply_to_message_id=message.id)
        
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
        
print("Robô iniciado.")
#print(fiis_cnpj)

#Thread(target=env, daemon=True).start()
bot.set_my_commands([telebot.types.BotCommand(comando[0], comando[1]) for comando in comandos])

bot.infinity_polling(timeout=200, long_polling_timeout = 5)