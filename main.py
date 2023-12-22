import pandas as pd

import requests
import telebot
#import pandas as pd
import time
import urllib
from threading import Thread
import threading
import re
   
from telethon import TelegramClient
import asyncio
from telethon.tl.types import DocumentAttributeVideo, InputMediaUploadedDocument

import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials

import datetime

import xmltodict

import time

from bs4 import BeautifulSoup

import pytz

import traceback

import concurrent.futures

from multiprocessing.pool import ThreadPool

import queue

import super_fiis_notificador as sfnot

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    #bot.send_message("-743953207", "pronto!")
    return "Hello Back4apper!"

@app.route('/kill')
def kill_app():
    os._exit(0)
    return "Killed"

def flask_thread():
   app.run(host='0.0.0.0', port=8080)

def request_flask_thread():
   while True:
      try:
         time.sleep(600)
         #bot.send_message("556068392", str(agora()))
         requests.get("https://superfiis1-gilmartaj.b4a.run/")
         #requests.get("https://aaa-2jrx.onrender.com/verificar")
         requests.get("https://aaa-2jrx.onrender.com")
      except:
         try:
            time.sleep(300)
         except:
            pass

Thread(target=flask_thread).start()

"""gspread_credentials = {
  "type": "service_account",
  "project_id": os.getenv("gspread_project_id"),
  "private_key_id": os.getenv("gspread_private_key_id"),
  "private_key": (os.getenv("gspread_private_key_1")+os.getenv("gspread_private_key_2")).replace(r"\n","\n"),
  "client_email": os.getenv("gspread_client_email"),
  "client_id": os.getenv("gspread_client_id"),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": os.getenv("gspread_client_x509_cert_url")
}"""

#print(gspread_credentials)

client = gspread.service_account(filename='superfiisbot-9f67df851d9a.json')
#client = gspread.service_account_from_dict(gspread_credentials)

sheet = client.open("SeguidoresFIIs").sheet1
sheet_infra = client.open("SeguidoresFI-Infras").sheet1

telebot.apihelper.SESSION_TIME_TO_LIVE = 60 * 15
"""
bot_aux = os.getenv("bot_aux_token")
bot_super = os.getenv("bot_super_token")

TELETHON_API_ID = os.getenv("telethon_api_id")
TELETHON_API_HASH = os.getenv("telethon_api_hash")
"""
bot_aux = os.getenv("BOT_AUX_TOKEN")
bot_super = os.getenv("BOT_SUPER_TOKEN")

TELETHON_API_ID = os.getenv("TELETHON_API_ID")
TELETHON_API_HASH = os.getenv("TELETHON_API_HASH")

bot = telebot.TeleBot(bot_super)

bot_url = "https://aaa-2jrx.onrender.com"

fila_doc = queue.Queue()

comandos = [
    ("start", "Iniciar"),
    ("ajuda", "Exibe a mensagem de ajuda."),
    ("cnpj", 'Exibe o CNPJ de um FII. Ex.: "/cnpj URPR11".'),
    ("contato", "Exibe informações para contato."),
    ("cotacao", 'Mostra a cotação de um fundo. Ex.: "/cotacao URPR11"'),
    ("docs", 'Receba os documentos emitidos pelo fundo nos últimos 30 dias. Ex.: "/docs URPR11"'),
    ("desinscrever", 'Use para deixar de seguir um FII que você segue. Ex.: "/desinscrever URPR11"'),
    ("doacao", "Ajude a manter o projeto vivo doando a partir de 1 centavo. Chave Pix: gil77891@gmail.com"),
    ("fundos_seguidos", "Lista todos os fundos imobiliários que você segue."),
    ("rend", 'Informa a última distribuição de proventos do fundo. Ex.: "/rend URPR11"'),
    ("seguir", 'Use para receber todos os documentos e informações de rendimentos de um FII. Ex.: "/seguir URPR11"'), 
    ("ultimos_documentos", 'Receba os documentos emitidos pelo fundo nos últimos 30 dias. Ex.: "/ultimos_documentos URPR11"'),
    ("mais", "Mais comandos..."),
    ]
    
mais_comandos = [
    ("fnet", "Link para a página de documentos referente a um fundo.\nEx.: /fnet CYCR11"),
    ("infm", "Use para receber o último informe mensal publicado por um fundo. \nEx.: /infm CYCR11"),
    ("inft", "Use para receber o último informe trimestral publicado por um fundo. \nEx.: /inft CYCR11"),
    ("pat", "Mostra informações sobre atualização patrimonial de um fundo.\nEx.: /pat CYCR11"),
    ("reg", "Use para receber o último regulamento publicado por um fundo. \nEx.: /reg CYCR11"),
    ("relat", "Use para receber o último relatório gerencial publicado por um fundo. \nEx.: /relat CYCR11"),
    ]

fiis_cnpj = pd.read_csv("fiis_cnpj.csv", dtype={"Código":str, "CNPJ":str}).dropna()
fiagros_cnpj = pd.read_csv("fiagros_cnpj.csv", dtype={"Código":str, "CNPJ":str}).dropna()
fidcs_cnpj = pd.read_csv("fidcs_cnpj.csv", dtype={"Código":str, "CNPJ":str}).dropna()
etfs_rf_cnpj = pd.read_csv("etfs-renda-fixa_cnpj.csv", dtype={"Código":str, "CNPJ":str}).dropna()
etfs_rv_cnpj = pd.read_csv("etfs-renda-variavel_cnpj.csv", dtype={"Código":str, "CNPJ":str}).dropna()
fiis_cnpj = pd.concat([fiis_cnpj, fiagros_cnpj, fidcs_cnpj,etfs_rf_cnpj,etfs_rv_cnpj])



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
        for f in self.planilha.keys():
            while self.planilha[f][-1] == "":
                del self.planilha[f][-1]
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
        return sorted(seguidos)
        
    def buscar_seguidores(self, fii):
        return list(filter(lambda s: s != "", self.planilha[fii]))
        #return ["556068392","-743953207"]
            
    def colunas(self):
        return sorted(self.planilha.keys())
        
    def buscar_todos_usuarios(self):
        seguidores = []
        for f in self.planilha.keys():
            for seg in self.buscar_seguidores(f):
                if seg not in seguidores:
                    seguidores.append(seg)
        return seguidores
 
base = BaseCache(sheet)
base_infra = BaseCache(sheet_infra)

import multiprocessing
lock = multiprocessing.Lock()
log_sheet = client.open("log").sheet1
def log(mensagem):
    try:
        lock.acquire(timeout=2)
    except:
        return
    try:
        #log_sheet.append_row([str(agora()), mensagem])
        with open("log.txt", "a") as log:
            log.write(f"[{agora()}] {mensagem}\n")
    except:
        pass
    try:
        lock.release()
    except:
        pass

def informar_proventos(doc, usuarios):
#422748
    r = requests.get(f'https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id={doc["id"]}', headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"})

    v_atual = 0

    try:
        v_atual = get_ticker_value(doc["codigoFII"])
    except:
        pass

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
                prov = float(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["ValorProvento"])
                mensagem += f'\n\U0001F4B0Rendimento: R$ {conv_monet(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["ValorProvento"])}'
                mensagem += f'\n\U0001F5D3Data base: {conv_data(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["DataBase"])}'
                mensagem += f'\n\U0001F4B8Data de pagamento: {conv_data(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["DataPagamento"])}'
                if v_atual and dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["CodNegociacao"] == doc["codigoFII"]:
                    mensagem += f'\n\uFF05 (preço atual): {prov/v_atual:.2%}'.replace(".",",")
            elif d == "Amortizacao":
                mensagem += f'\n\n\U0001F3E0Código: {dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["CodNegociacao"]}'
                print(float(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Amortizacao"]["ValorProvento"]))
                mensagem += f'\n\U0001F4B0Amortização: R$ {conv_monet(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Amortizacao"]["ValorProvento"])}'
                mensagem += f'\n\U0001F5D3Data base: {conv_data(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Amortizacao"]["DataBase"])}'
                mensagem += f'\n\U0001F4B8Data de pagamento: {conv_data(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Amortizacao"]["DataPagamento"])}'
        else:
            print(d["CodNegociacao"])
            
            for d2 in d:
                if d2 == "Rendimento":
                    mensagem += f'\n\n\U0001F3E0Código: {d["CodNegociacao"]}'
                    print(float(d[d2]["ValorProvento"]))
                    prov = float(d[d2]["ValorProvento"])
                    mensagem += f'\n\U0001F4B0Rendimento: R$ {conv_monet(d[d2]["ValorProvento"])}'
                    mensagem += f'\n\U0001F5D3Data base: {conv_data(d[d2]["DataBase"])}'
                    mensagem += f'\n\U0001F4B8Data de pagamento: {conv_data(d[d2]["DataPagamento"])}'
                    if v_atual and d["CodNegociacao"] == doc["codigoFII"]:
                        mensagem += f'\n\uFF05 (preço atual): {prov/v_atual:.2%}'.replace(".",",")
                elif d2 == "Amortizacao":
                    mensagem += f'\n\n\U0001F3E0Código: {d["CodNegociacao"]}'
                    print(d[d2]["ValorProvento"])
                    mensagem += f'\n\U0001F4B0Amortização: R$ {conv_monet(d[d2]["ValorProvento"])}'
                    mensagem += f'\n\U0001F5D3Data base: {conv_data(d[d2]["DataBase"])}'
                    mensagem += f'\n\U0001F4B8Data de pagamento: {conv_data(d[d2]["DataPagamento"])}'
        #print(mensagem)
        
        
    mensagem += "\n\n@RepositorioDeFIIs"
    print(mensagem)
    for u in usuarios:
        try:
            bot.send_message(u, mensagem)
        except:
            pass

def capitalizar(texto):
    return " ".join(map(lambda p: p.capitalize(), texto.split())).strip()

def get_nome_pelo_isin(fundo, cod_isin):
    fundos = pd.read_csv("isins_tokens.csv").dropna()
    token = fundos.where(fundos["Código"] == fundo).dropna()["Token"].values[0]
    r = requests.get(f"https://sistemaswebb3-listados.b3.com.br/isinProxy/IsinCall/GetEmitterCode/{token}")
    print(cod_isin, r.json()["results"])
    for isin in r.json()["results"]:
        if isin["isin"] != cod_isin:
            continue
        #if isin["codigoEmissor"].split().upper() != fundo[:4]:
            #raise Exception()
        if isin["descricaoPt"].strip().upper() in ("COTAS","COTAS - COTAS"):
            return fundo
        regex = re.compile(isin["codigoEmissor"]+r"\d\d")
        busca = regex.search(isin["descricaoPt"])
        #print(isin)
        if busca:
            return busca.group() 
        else:
            #return (fundo + " (" + isin["descricaoPt"].strip() + ")").replace("COTAS - COTAS", "COTAS -")
            return fundo + " (" + capitalizar(isin["descricaoPt"].strip().replace("COTAS - COTAS", "COTAS")) + ")"
    return cod_isin
            
def buscar_ultimo_provento_infra(fundo):
    r = requests.get("https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/GetListedSupplementFunds/"+tokens_infra[fundo])
    
    prov = None
    results = r.json()["cashDividends"]
    for d in results:
        #print(d)
        isin = d["isinCode"]
        if isin[6:9] != "CTF":
            continue
        if prov != None:
            if prov["dataBase"] == d["lastDatePrior"] and prov["dataPagamento"] == d["paymentDate"]:
                prov["valor"] = str(float(prov["valor"]) + float(d["rate"].replace(",",".")))
                if len(prov["valor"].split(".")[-1]) > 11:
                    prov["valor"] = f'{float(prov["valor"]):.11f}'
            else:
                break
        else:
            prov = {"codigo": fundo, "valor": d["rate"].replace(",","."), "competencia": d["relatedTo"].lower(), "dataBase": d["lastDatePrior"], "dataPagamento": d["paymentDate"]}
    return prov
    
def buscar_ultimo_provento_infra(fundo):
    r = requests.get("https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/GetListedSupplementFunds/"+tokens_infra[fundo])
    
    prov = {}
    results = r.json()["cashDividends"]
    for d in results:
        print(prov)
        #print(d)
        isin = d["isinCode"].strip()
        if isin in prov:
            if prov[isin]["dataBase"] == d["lastDatePrior"] and prov[isin]["dataPagamento"] == d["paymentDate"]:
                prov[isin]["valor"] = str(float(prov[isin]["valor"]) + float(d["rate"].replace(",",".")))
                if len(prov[isin]["valor"].split(".")[-1]) > 11:
                    prov[isin]["valor"] = f'{float(prov["valor"]):.11f}'
            else:
                break
        else:
            if len(prov.keys()) > 0 and (prov[list(prov.keys())[0]]["dataBase"] != d["lastDatePrior"] or prov[list(prov.keys())[0]]["dataPagamento"] != d["paymentDate"]):
                break
            prov[isin] = {"codigo": fundo, "valor": d["rate"].replace(",","."), "competencia": d["relatedTo"].lower(), "dataBase": d["lastDatePrior"], "dataPagamento": d["paymentDate"]}
    for isin in prov.keys():
        prov[isin]["codigo"] = get_nome_pelo_isin(prov[isin]["codigo"], isin)
    return list(map(lambda x: x[1], list(sorted(prov.items(), key=lambda x:x[0]))))
        
def comparar_proventos_infra(p1, p2):
    if not p2:
        return True
    if not p1:
        return False
    if len(p1) != len(p2):
        return False
    for i in range(len(p1)):
        if p1[i]["valor"] != p2[i]["valor"] or p1[i]["competencia"] != p2[i]["competencia"] or p1[i]["dataBase"] != p2[i]["dataBase"] or p1[i]["dataPagamento"] != p2[i]["dataPagamento"]:
            return False
        try:
            if datetime.datetime.strptime(p2, '%d/%m/%Y') < datetime.datetime.strptime(p1, '%d/%m/%Y'):
                return True
        except:
            pass
    return True
    
def informar_provento_infra1(info, seguidores):
    mensagem = "Informação de distribuição:"
    mensagem += f'\n\n\U0001F3D7Código: {info["codigo"]}'
    mensagem += f'\n\U0001F4CBRef.: {info["competencia"]}'
    mensagem += f'\n\n\U0001F4B0Valor: R$ {conv_monet(info["valor"])}'
    mensagem += f'\n\U0001F5D3Data base: {info["dataBase"]}'
    mensagem += f'\n\U0001F4B8Data de pagamento: {info["dataPagamento"]}'
    
    mensagem += "\n\n@SuperFIIsBot\n@RepositorioDeFIIs"
    
    #usuarios = ["556068392","-743953207","556068392"]
    for u in seguidores:
        try:
            bot.send_message(u, mensagem)
        except:
            try:
                bot.send_message(u, mensagem)
            except:
                pass   

def informar_provento_infra1(infos, seguidores):
    mensagem = "Informação de distribuição:"
    mensagem += f'\n\U0001F4CBRef.: {infos[0]["competencia"]}'
    
    for info in infos:
        mensagem += f'\n\n\U0001F3D7Código: {info["codigo"]}'
        mensagem += f'\n\U0001F4B0Valor: R$ {conv_monet(info["valor"])}'
        mensagem += f'\n\U0001F5D3Data base: {info["dataBase"]}'
        mensagem += f'\n\U0001F4B8Data de pagamento: {info["dataPagamento"]}'
    
    mensagem += "\n\n@SuperFIIsBot\n@RepositorioDeFIIs"
    
    #usuarios = ["556068392","-743953207","556068392"]
    for u in seguidores:
        try:
            bot.send_message(u, mensagem)
        except:
            try:
                bot.send_message(u, mensagem)
            except:
                pass         


def informar_fechamento2():
    dic = {}
    usuarios = base.buscar_todos_usuarios()
    usuarios.extend(base_infra.buscar_todos_usuarios())
    usuarios = list(set(usuarios))
    usuarios.remove("-1001894911077")
    usuarios.append("-1001894911077")
    #usuarios.insert(0, "556068392")
    #usuarios = ["556068392"]
    print(usuarios)

    for usuario in usuarios:#usuarios:#base.buscar_todos_seguidores:
        fs = base.buscar_seguidos(usuario)
        fs.extend(base_infra.buscar_seguidos(usuario))
        fs.sort()
        if len(fs) == 0:
            continue
        msg = mensagem_lista_fechamento(fs, dic)
        if msg:
            h = agora()
            try:
                if len(msg) <= 3850:
                    msg = f"\U0001F6AAFECHAMENTO ({h.day:02d}/{h.month:02d}/{h.year})\n" + msg + "\n\n@SuperFIIsBot"
                    bot.send_message(usuario, msg)
                else:
                    msg1 = f"\U0001F6AAFECHAMENTO ({h.day:02d}/{h.month:02d}/{h.year})\n" + msg[:msg.index("\n", 3300)] + "\n\n@RepositorioDeFIIs\n@SuperFIIsBot"
                    bot.send_message(usuario, msg1)
                    msg2 = f"\U0001F6AAFECHAMENTO ({h.day:02d}/{h.month:02d}/{h.year})\n" + msg[msg.index("\n", 3300):msg.index("\n", 6600)] + "\n\n@RepositorioDeFIIs\n@SuperFIIsBot"
                    bot.send_message(usuario, msg2)
                    msg3 = f"\U0001F6AAFECHAMENTO ({h.day:02d}/{h.month:02d}/{h.year})\n" + msg[msg.index("\n", 6600):] + "\n\n@RepositorioDeFIIs\n@SuperFIIsBot"
                    bot.send_message(usuario, msg3)
            except:
                pass
            

def mensagem_lista_fechamento(fundos, dic):  
    if len(fundos) > 0:
        msg = "" 
        for f in fundos:
            try:
                print(f)
                if f in dic and dic[f][0] and dic[f][1]:
                    v, variacao = dic[f]
                    #print("Já lá")
                else:
                    v, variacao = get_ticker_variacao3(f)
                    time.sleep(5)
                    if not v or v.startswith("0,00"):
                        continue
                    dic[f] = (v, variacao)
                l = f"{f}: R$ {v}".replace(".",",")
                print(variacao)
                if variacao:
                    l += f" ({variacao})"
                    if variacao.startswith("+"):
                        l = "\U0001F7E2" + l
                    elif variacao.startswith("−") or variacao.startswith("-"):
                        l = "\U0001F53B" + l
                    else:
                        #print("else")
                        l = "\u2B1C" + l
                else:
                    l = "\u26AB" + l
                msg += "\n"+l
            except Exception:
                pass#traceback.print_exc()
    
    #print(msg)            
    return msg

def informar_fechamento(fundos, usuario):
    h = agora()
    msg = f"Fechamento ({h.day:02d}/{h.month:02d}/{h.year})\n"
    
    if len(fundos) > 0:
    
        for f in fundos:
            try:
                print(f)
                v = get_ticker_value(f)
                l = f"{f}: R$ {v:.2f}".replace(".",",")
                variacao = get_variacao(f)
                print(variacao)
                if variacao:
                    l += f" ({variacao}%)"
                    if variacao.startswith("+"):
                        l = "\U0001F7E2" + l
                    elif variacao.startswith("−") or variacao.startswith("-"):
                        l = "\U0001F53B" + l
                    else:
                        print("else")
                        l = "\u2B1C" + l
                else:
                    l = "\u26AB" + l
                msg += "\n"+l
            except:
                pass
                
        msg += "\n\n@SuperFIIsBot"
        
        bot.send_message(usuario, msg)
        
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
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=1&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}", timeout=30)
    lista = []
    for d in r.json()["data"]:
        de = d["dataEntrega"]
        #print(datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13])), desde)
        if datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13]), minute=int(de[14:16]), tzinfo=tz_info) <= desde:
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
        #print(datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13])), desde)
        if datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13]), minute=int(de[14:16])) < desde:
            break
        if d["status"] == "AC":
            lista.append(d)
    lista.reverse()
    return lista
    

def buscar_documentos_infra(token, desde=""):
    r = requests.get(f"https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/GetListedPreviousDocuments/{token}")
    #print(f"https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/GetListedPreviousDocuments/{token}")
    lista = []
    results = r.json()["results"]
    for d in results:
        de = d["date"]
        #print(datetime.datetime(year=int(de[0:4]), month=int(de[5:7]), day=int(de[8:10]), hour=int(de[11:13]), minute=int(de[14:16])), desde)
        if datetime.datetime(year=int(de[0:4]), month=int(de[5:7]), day=int(de[8:10]), hour=int(de[11:13]), minute=int(de[14:16]), tzinfo=tz_info) <= desde:
            break
        lista.append(d)
        print(d)
    lista.reverse()
    return lista
    
def buscar_ultimo_relatorio_infra(fundo):
    r = requests.get(f"https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/GetListedPreviousDocuments/{tokens_infra[fundo]}")

    results = r.json()["results"]
    for d in results:
        nome = d["name"]
        if "relatório" in nome.lower() or "relatorio" in nome.lower() or fundo == "KDIF11" and "carta do gestor" in nome.lower():
            return d
    return None
    
async def enviar_documento_1(usuario, nome_doc, caption,client):
    
        with open(nome_doc, "rb") as fp:
            z = await client.send_file(usuario, file=fp, caption=caption)
            return z.file.id
            
def compartilhar_documento_enviado(usuarios, file_id, caption):
    for u in usuarios:
        try:
            bot.send_document(
            u,
            file_id,
            caption=caption
            )
            time.sleep(0.1)
        except:
            pass

def baixar_documento_1(link, nome_doc, cabecalhos={}):
    with open(nome_doc, "wb") as f:
        f.write(requests.get(link, headers=cabecalhos).content)
            
def env_infra(cod_fundo, doc, usuarios):
    if len(usuarios) < 1:
        return
      
    nome_doc = cod_fundo + " - " + doc["name"].replace("/","_") + ".pdf"
    link = f'https://bvmf.bmfbovespa.com.br/sig/FormConsultaPdfDocumentoFundos.asp?strSigla={cod_fundo[:-2]}&strData={doc["date"]}'
    baixar_documento_1(link, nome_doc, cabecalhos={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"})
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    file_id = 0
    caption = cod_fundo + " - " + doc["name"] + "\n\n@RepositorioDeFIIs\n@SuperFiisBot"
    with TelegramClient("bot", TELETHON_API_ID, TELETHON_API_HASH).start(bot_token=bot_super) as client:
        x = loop.run_until_complete(asyncio.wait([enviar_documento_1(int(usuarios[0]), nome_doc, caption, client)]))
        file_id = list(x[0])[0].result()
    os.remove(nome_doc)
    print(file_id)
    if len(usuarios) > 1:
        compartilhar_documento_enviado(usuarios[1:], file_id, caption)

    
"""def buscar_ultimo_documento_provento(cnpj):
    rend = None
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=1&s=0&l=100&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}")
    for d in r.json()["data"]:
        tipo = d["tipoDocumento"]
        #print(datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13])), desde)
        if tipo.strip() == "Rendimentos e Amortizações":
            return d
    return None"""
def buscar_ultimo_documento_provento(cnpj):
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=0&s=0&l=1&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}&idCategoriaDocumento=14&idTipoDocumento=41")
    if len(r.json()["data"]) > 0:
        return r.json()["data"][0]
    return None
    
def buscar_ultimo_informe_mensal_estruturado(cnpj):
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=0&s=0&l=1&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}&idCategoriaDocumento=6&idTipoDocumento=40")
    if len(r.json()["data"]) > 0:
        return r.json()["data"][0]
    return None
    
def buscar_ultimo_informe_trimestral_estruturado(cnpj):
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=0&s=0&l=1&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}&idCategoriaDocumento=6&idTipoDocumento=45")
    if len(r.json()["data"]) > 0:
        return r.json()["data"][0]
    return None
    
    
def buscar_ultimo_relatorio_gerencial(cnpj):
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=0&s=0&l=1&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}&idCategoriaDocumento=7&idTipoDocumento=9")
    if len(r.json()["data"]) > 0:
        print("Enc")
        return r.json()["data"][0]
    return None
    
def buscar_ultimo_regulamento(cnpj):
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=0&s=0&l=1&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}&idCategoriaDocumento=5")
    if len(r.json()["data"]) > 0:
        return r.json()["data"][0]
    return None
        
def baixarDocumento(link):
    pass

def envio_multiplo(doc, file_id, usuarios, caption_):
    for u in usuarios:
        try:
            bot.send_document(
            u,
            file_id,
            visible_file_name="Informe.pdf",
            caption=caption_
            )
            time.sleep(0.05)
        except:
            try:
                bot.send_document(
                u,
                file_id,
                visible_file_name="Informe.pdf",
                caption=caption_
                )
                time.sleep(0.05)
            except:
                try:
                    bot.send_message("-743953207", f"ERRO: {u}")
                except:
                    print(f"ERRO: {u}")
                    
def envio_multiplo_telebot(doc, usuarios, caption_):
    if len(usuarios) <= 0:
        return
    
    try:    
        dx = bot.send_document(
                usuarios[0],
                xml_pdf(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}'),
                visible_file_name="Informe.pdf",
                caption=caption_
                )
    except:
        try:    
            dx = bot.send_document(
                usuarios[0],
                xml_pdf(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}'),
                visible_file_name="Informe.pdf",
                caption=caption_
                )
        except:
            try:
                bot.send_message("-743953207", f"ERRO: {usuarios[0]}")
            except:
                print(f"ERRO: {usuarios[0]}")
            return
    if len(usuarios) > 1:        
        envio_multiplo(doc, dx.document.file_id, usuarios[1:], caption_)
        
def envio_multiplo_telethon(doc, usuarios):
    if len(usuarios) <= 0:
        return
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tipo_doc = doc["tipoDocumento"].replace("/", "-") if doc["tipoDocumento"].strip() != "" else doc["categoriaDocumento"]
    if doc["tipoDocumento"].strip() == "AGO" or doc["tipoDocumento"].strip() == "AGE":
                tipo_doc = doc["categoriaDocumento"].replace("/", "-").strip() + " - " + doc["tipoDocumento"].replace("/", "-").strip() + " - " + doc["especieDocumento"].replace("/", "-").strip()
    with TelegramClient("bot", TELETHON_API_ID, TELETHON_API_HASH).start(bot_token=bot_super) as client:
     with open(f'{doc["codigoFII"]} - {tipo_doc}.pdf', "wb") as f:
        f.write(requests.get(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}', headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"}).content)
        try:
            loop.run_until_complete(asyncio.wait([ enviar_documento( doc, int(usuarios[0]), client)]))
        except:
            loop.run_until_complete(asyncio.wait([ enviar_documento( doc, int(usuarios[0]), client)]))
        #print("id", doc["file_id"])
        #print("LLLLLLLLLLLLLLLL")
     os.remove(f'{doc["codigoFII"]} - {tipo_doc}.pdf')
    #print(len(usuarios))
    if len(usuarios) > 1:
        tipo_doc = doc["tipoDocumento"].replace("/", "-") if doc["tipoDocumento"].strip() != "" else doc["categoriaDocumento"]
        if doc["tipoDocumento"].strip() == "AGO" or doc["tipoDocumento"].strip() == "AGE":
            tipo_doc = doc["categoriaDocumento"].replace("/", "-").strip() + " - " + doc["tipoDocumento"].replace("/", "-").strip() + " - " + doc["especieDocumento"].replace("/", "-").strip()
        if tipo_doc == "Relatório Gerencial":
            data_ref = re.search(r"\d\d/\d\d\d\d", doc["dataReferencia"])
        else:
            data_ref = re.search(r"\d\d/\d\d/\d\d\d\d", doc["dataReferencia"])
        data_ref = "("+data_ref.group()+")" if data_ref else doc["dataReferencia"].replace("/", "-").replace(":", "-")     
        envio_multiplo(doc, doc["file_id"], usuarios[1:], f'{doc["codigoFII"]} - {tipo_doc} {data_ref}\n\n@RepositorioDeFIIs')

def env2(doc, usuarios):
    if doc["categoriaDocumento"] in ("Informes Periódicos", "Aviso aos Cotistas - Estruturado") and doc["tipoDocumento"] != "Demonstrações Financeiras" or "Estruturado" in doc["tipoDocumento"] or "Formulário de Liberação para Negociação das Cotas" in doc["tipoDocumento"]:
        data_ref = re.search(r"\d\d/\d\d\d\d", doc["dataReferencia"])
        data_ref = "("+data_ref.group()+")" if data_ref else doc["dataReferencia"].replace("/", "-").replace(":", "-")
        envio_multiplo_telebot(doc, usuarios, f'{doc["codigoFII"]} - {doc["tipoDocumento"]} {data_ref}\n\n@RepositorioDeFIIs')
    else:
        envio_multiplo_telethon(doc, usuarios)
  
def env(doc, usuario):
        if doc["categoriaDocumento"] in ("Informes Periódicos", "Aviso aos Cotistas - Estruturado") and doc["tipoDocumento"] != "Demonstrações Financeiras" or "Estruturado" in doc["tipoDocumento"] or "Formulário de Liberação para Negociação das Cotas" in doc["tipoDocumento"]:
            data_ref = re.search(r"\d\d/\d\d\d\d", doc["dataReferencia"])
            data_ref = "("+data_ref.group()+")" if data_ref else doc["dataReferencia"].replace("/", "-").replace(":", "-")
            dx = bot.send_document(
            usuario,
            xml_pdf(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}'),
            visible_file_name="Arquivo.pdf",
            caption=f'{doc["codigoFII"]} - {doc["tipoDocumento"]} {data_ref}\n\n@SuperFIIsBot'
            )
            #print(dx.document.file_id)
        else:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tipo_doc = doc["tipoDocumento"].replace("/", "-") if doc["tipoDocumento"].strip() != "" else doc["categoriaDocumento"]
            if doc["tipoDocumento"].strip() == "AGO" or doc["tipoDocumento"].strip() == "AGE":
                tipo_doc = doc["categoriaDocumento"].replace("/", "-").strip() + " - " + doc["tipoDocumento"].replace("/", "-").strip() + " - " + doc["especieDocumento"].replace("/", "-").strip()
            with TelegramClient("bot", TELETHON_API_ID, TELETHON_API_HASH).start(bot_token=bot_super) as client:
             with open(f'{doc["codigoFII"]} - {tipo_doc}.pdf', "wb") as f:
                f.write(requests.get(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}', headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"}).content)
                loop.run_until_complete(asyncio.wait([ enviar_documento( doc, usuario, client)]))
             os.remove(f'{doc["codigoFII"]} - {tipo_doc}.pdf')
           
   
async def enviar_documento(doc, usuario, client):
    #doc_id 430265
    tipo_doc = doc["tipoDocumento"].replace("/", "-") if doc["tipoDocumento"].strip() != "" else doc["categoriaDocumento"]
    if doc["tipoDocumento"].strip() == "AGO" or doc["tipoDocumento"].strip() == "AGE":
        tipo_doc = doc["categoriaDocumento"].replace("/", "-").strip() + " - " + doc["tipoDocumento"].replace("/", "-").strip() + " - " + doc["especieDocumento"].replace("/", "-").strip()
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
            #requests.post(f"http://api.telegram.org/bot{bot_super_token}/sendDocument", files=files, data=values)
            
            #bot.send_document(556068392,open("/home/gilmartaj/SuperFIIs/Documento.pdf", "rb"), timeout=200)
            with open(f'{doc["codigoFII"]} - {tipo_doc}.pdf', "rb") as fp:
                    z = await client.send_file(usuario, file=fp, caption=f'{doc["codigoFII"]} - {tipo_doc} {data_ref}\n\n@RepositorioDeFIIs')
                    #print("ID:", z.file.id)
                    #telebot.TeleBot(bot_super).send_document(usuario, z.file.id, caption="TESTE")
                    doc["file_id"] = z.file.id
    
def buscar_cnpj(codigo_fii):
    return fiis_cnpj.where(fiis_cnpj["Código"] == codigo_fii).dropna().iloc[0]["CNPJ"]


def xml_pdf(link):

    link = link.replace("https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=", bot_url+"/fnet_arq/")

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

    #print(server_file)

    #sys.exit(0)

    preview = requests.post(f"https://api32.ilovepdf.com/v1/preview", headers=h2, data=f'-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="server_filename"\r\n\r\n{server_file}\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="task"\r\n\r\nw3xjsv3pgkt1hklngy36z0v2q0pdhv01rpx7brwwyxd7AAztccm2p3g9nkwq6gbc2085df55v058qyx32lsktAg8mvtmxlxm1zj3h1h20gvtkgdmr6dy5mnlkkntqgAdk7ssy1z9yq00bjm42rfzlv6qpw4b1yp48Av3mggqA60rg7p7zygq\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="page_orientation"\r\n\r\nportrait\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="page_margin"\r\n\r\n0\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="url"\r\n\r\nhttps://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id=430731&cvm=true&#toolbar=0\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="view_width"\r\n\r\n768\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="page_size"\r\n\r\nA4\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="single_page"\r\n\r\ntrue\r\n-----------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="block_ads"\r\n\r\nfalse\r\n-----server------------------------60486432820756574052288473281\r\nContent-Disposition: form-data; name="remove_popups"\r\n\r\nfalse\r\n-----------------------------60486432820756574052288473281--\r\n'.encode("utf-8")).json()["thumbnail"]

    return f'https://api32.ilovepdf.com/thumbnails/{preview}'


"""r = requests.get("https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=1&s=0&l=2&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo=11179118000145")

bot = telebot.TeleBot(bot_super)

print(r.json()["data"][1]["dataEntrega"])


remote_url = f'https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id={r.json()["data"][1]["id"]}'
# Define the local filename to save data
local_file = f'{r.json()["data"][1]["tipoDocumento"]} {r.json()["data"][1]["dataReferencia"][-7:].replace("/","-")} - {r.json()["data"][1]["descricaoFundo"]}.pdf'

open(local_file, "wb").write(requests.get(remote_url, headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"}).content)
"""

@bot.message_handler(commands=["teste"])
def handle_command(message):
    print(message.text)
    #with open('/home/gilmartaj/SuperFIIs/Relatório Gerencial 02-2023 - FII ANHANGUERA EDUCACIONAL.pdf', 'rb') as f:
    """bot.send_document(
    message.from_user.id,
    'https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id=430265',
    visible_file_name="Relatório.pdf",
    caption="2023"
    )"""
    
    #informar_fechamento(("MCHF11", "HCTR11", "APTO11", "CYCR11", "FAED11", "HGIC11", "MCHF11", "RZAT11", "URPR11", "VGHF11","KIVO11", "LIFE11", "MCHY11", "MFCR11", "MGHT11", "PLOG11", "RPRI11", "KINP11"), message.from_user.id)
    
    """print("\n\n\nbbbb\n\n\n")
    for fii in ("MCHF11", "HCTR11", "APTO11", "CYCR11", "FAED11", "HGIC11", "MCHF11", "RZAT11", "URPR11", "VGHF11","KIVO11", "LIFE11", "MCHY11", "MFCR11", "MGHT11", "PLOG11", "RPRI11", "KINP11"):
        aaa = buscar_documentos2(buscar_cnpj(fii), datetime.datetime.now()-datetime.timedelta(days=1))
        
        
        for a in aaa:
            print(fii, "-", a["tipoDocumento"])
            
            a["codigoFII"] = fii
            #Thread(target=enviar_documento, args=(a, message.from_user.id), daemon=True).start()
            #bot.set_my_commands([telebot.types.BotCommand(comando[0], comando[1]) for comando in comandos])
            env(a, message.from_user.id)
            if a["tipoDocumento"] == "Rendimentos e Amortizações":
                informar_proventos(a, message.from_user.id)
    bot.send_message(message.from_user.id, "https://www.seudinheiro.com/2023/bolsa-dolar/ameaca-de-novo-calote-derruba-cotas-de-cinco-fundos-imobiliarios-na-b3-lvit/")"""
    """try:
        ticker = message.text.split()[1].strip().upper()
        val, var = get_ticker_variacao3(ticker)
        bot.send_message(message.chat.id, str(val)+"\n"+str(var), reply_to_message_id=message.id)
    except:
        traceback.print_exc()"""
    """doc_rend = buscar_ultimo_documento_provento(buscar_cnpj(ticker))
    if doc_rend:
        doc_rend["codigoFII"] = ticker
        informar_proventos(doc_rend, message.from_user.id)
    else:
        bot.send_message(message.chat.id, f'Não encontramos informações sobre a última distribuição deste fundo.', reply_to_message_id=message.id)"""
    ticker = message.text.split()[1].strip().upper()
    """prov = buscar_ultimo_provento_infra(ticker)
    if prov != None:
        informar_provento_infra1(prov, [message.from_user.id])
    else:
        bot.send_message(message.chat.id, "Não encontramos informações sobre a última distribuição deste fundo.", reply_to_message_id=message.id)
    prov2 = buscar_ultimo_provento_infra("CDII11")
    print(prov == prov2)"""


@bot.message_handler(commands=["rend"])
def handle_command(message):
    #cmd = message.text.split()[0]
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        if not ticker in base.colunas():
            #if ticker in ("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
            if ticker in tokens_infra.keys():
                #bot.send_message(message.chat.id, f"Desculpe, mas no momento esta função não está disponível para FI-Infras.", reply_to_message_id=message.id)
                enviada = bot.send_message(message.chat.id, f"Buscando...")
                prov = buscar_ultimo_provento_infra(ticker)
                if prov != None:
                    informar_provento_infra1(prov, [message.from_user.id])
                else:
                    bot.send_message(message.chat.id, "Ocorreu um erro, tente novamente mais tarde.", reply_to_message_id=message.id)
                bot.delete_message(message.chat.id, enviada.id)
                return
            #else:
                #bot.send_message(message.chat.id, f"Por enquanto esta função não está disponível para FIPs.", reply_to_message_id=message.id)
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo {ticker}.", reply_to_message_id=message.id)
            return
        #enviada = bot.send_message(message.chat.id, f"Buscando...")
        doc_rend = buscar_ultimo_documento_provento(buscar_cnpj(ticker))
        if doc_rend:
            doc_rend["codigoFII"] = ticker
            informar_proventos(doc_rend, [message.from_user.id])
        else:
            bot.send_message(message.chat.id, f'Não encontramos informações sobre a última distribuição de proventos deste fundo.', reply_to_message_id=message.id)    
        #bot.delete_message(message.chat.id, enviada.id)
    elif len(message.text.strip().split()) == 1:
        bot.send_message(message.chat.id, f'Informe o código de negociação do fundo que você deseja ver informações sobre a última distribuições de proventos.\nEx.: "/rend URPR11".', reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Uso incorreto. Para ver informações sobre a última distribuição de proventos de um fundo, envie /rend CODIGO_FUNDO.\nEx.: "/rend URPR11".', reply_to_message_id=message.id)
        
@bot.message_handler(commands=["pat"])
def handle_command(message):
    #cmd = message.text.split()[0]
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    try:
        if len(message.text.strip().split()) == 2:
            ticker = message.text.split()[1].strip().upper()
            if not ticker in base.colunas():
                if ticker in tokens_infra.keys():
                    if ticker in ("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                        enviada = bot.send_message(message.chat.id, f"Buscando...")
                        informar_atualizacao_patrimonial_infra(ticker, [message.from_user.id])
                        bot.delete_message(message.chat.id, enviada.id)
                    else:
                        enviada = bot.send_message(message.chat.id, f"Buscando...")
                        informar_atualizacao_patrimonial_fip(ticker, [message.from_user.id])
                        bot.delete_message(message.chat.id, enviada.id)
                    return
                bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo {ticker}.", reply_to_message_id=message.id)
                return
            enviada = bot.send_message(message.chat.id, f"Buscando...")
            doc_pat = buscar_ultimo_informe_mensal_estruturado(buscar_cnpj(ticker))
            if doc_pat:
                doc_pat["codigoFII"] = ticker
                informar_atualizacao_patrimonial(doc_pat, [message.from_user.id])
            else:
                bot.send_message(message.chat.id, f'Não encontramos informações sobre a atualização patrimonial deste fundo.', reply_to_message_id=message.id)    
            bot.delete_message(message.chat.id, enviada.id)
        elif len(message.text.strip().split()) == 1:
            bot.send_message(message.chat.id, f'Informe o código de negociação do fundo que você deseja ver informações sobre a atualização patrimonial.\nEx.: "/pat URPR11".', reply_to_message_id=message.id)
        else:
            bot.send_message(message.chat.id, f'Uso incorreto. Para ver informações sobre a atualização patrimoniall de um fundo, envie /pat CODIGO_FUNDO.\nEx.: "/pat URPR11".', reply_to_message_id=message.id)
    except:
        traceback.print_exc()
        bot.send_message(message.chat.id, "Desculpe-nos, mas correu um erro. Tente novamente mais tarde.", reply_to_message_id=message.id)
    
@bot.message_handler(commands=["relat"])
def handle_command(message):
    #cmd = message.text.split()[0]
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        if not ticker in base.colunas():
            if ticker in tokens_infra.keys():#("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                #bot.send_message(message.chat.id, f"Desculpe, mas no momento esta função não está disponível para FI-Infras.", reply_to_message_id=message.id)
                enviada = bot.send_message(message.chat.id, f"Buscando...")
                doc = buscar_ultimo_relatorio_infra(ticker)
                if doc:
                    env_infra(ticker, doc, [message.from_user.id])
                else:
                    bot.send_message(message.chat.id, f'Não encontramos informações sobre relatórios gerenciais deste fundo.', reply_to_message_id=message.id)
                bot.delete_message(message.chat.id, enviada.id)
                return
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo {ticker}.", reply_to_message_id=message.id)
            return
        enviada = bot.send_message(message.chat.id, f"Buscando...")
        doc_relat = buscar_ultimo_relatorio_gerencial(buscar_cnpj(ticker))
        if doc_relat:
            doc_relat["codigoFII"] = ticker
            env2(doc_relat, [message.from_user.id])
        else:
            bot.send_message(message.chat.id, f'Não encontramos informações sobre relatórios gerenciais deste fundo.', reply_to_message_id=message.id)    
        bot.delete_message(message.chat.id, enviada.id)
    elif len(message.text.strip().split()) == 1:
        bot.send_message(message.chat.id, f'Informe o código de negociação do fundo que você deseja ver o último relatório gerencial publicado.\nEx.: "/relat CYCR11".', reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Uso incorreto. Para ver o último relatório gerencial de um fundo, envie /relat CODIGO_FUNDO.\nEx.: "/relat CYCR11".', reply_to_message_id=message.id)
        
@bot.message_handler(commands=["infm"])
def handle_command(message):
    #cmd = message.text.split()[0]
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        if not ticker in base.colunas():
            if ticker in tokens_infra.keys():#("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                bot.send_message(message.chat.id, f"Desculpe, mas no momento esta função não está disponível para FI-Infras.", reply_to_message_id=message.id)
                return
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo {ticker}.", reply_to_message_id=message.id)
            return
        enviada = bot.send_message(message.chat.id, f"Buscando...")
        doc_infm = buscar_ultimo_informe_mensal_estruturado(buscar_cnpj(ticker))
        if doc_infm:
            doc_infm["codigoFII"] = ticker
            env2(doc_infm, [message.from_user.id])
        else:
            bot.send_message(message.chat.id, f'Não encontramos informações sobre informes mensais deste fundo.', reply_to_message_id=message.id)    
        bot.delete_message(message.chat.id, enviada.id)
    elif len(message.text.strip().split()) == 1:
        bot.send_message(message.chat.id, f'Informe o código de negociação do fundo que você deseja ver o último informe mensal publicado.\nEx.: "/infm CYCR11".', reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Uso incorreto. Para ver o último informe mensal de um fundo, envie /infm CODIGO_FUNDO.\nEx.: "/infm CYCR11".', reply_to_message_id=message.id)
        
@bot.message_handler(commands=["inft"])
def handle_command(message):
    #cmd = message.text.split()[0]
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        if not ticker in base.colunas():
            if ticker in tokens_infra.keys():#("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                bot.send_message(message.chat.id, f"Desculpe, mas no momento esta função não está disponível para FI-Infras.", reply_to_message_id=message.id)
                return
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo {ticker}.", reply_to_message_id=message.id)
            return
        enviada = bot.send_message(message.chat.id, f"Buscando...")
        doc_inft = buscar_ultimo_informe_trimestral_estruturado(buscar_cnpj(ticker))
        if doc_inft:
            doc_inft["codigoFII"] = ticker
            env2(doc_inft, [message.from_user.id])
        else:
            bot.send_message(message.chat.id, f'Não encontramos informações sobre informes trimestrais deste fundo.', reply_to_message_id=message.id)    
        bot.delete_message(message.chat.id, enviada.id)
    elif len(message.text.strip().split()) == 1:
        bot.send_message(message.chat.id, f'Informe o código de negociação do fundo que você deseja ver o último informe trimestral publicado.\nEx.: "/inft CYCR11".', reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Uso incorreto. Para ver o último informe trimestral de um fundo, envie /inft CODIGO_FUNDO.\nEx.: "/inft CYCR11".', reply_to_message_id=message.id)

@bot.message_handler(commands=["reg"])
def handle_command(message):
    #cmd = message.text.split()[0]
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        if not ticker in base.colunas():
            if ticker in tokens_infra.keys():#("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                bot.send_message(message.chat.id, f"Desculpe, mas no momento esta função não está disponível para FI-Infras.", reply_to_message_id=message.id)
                return
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo {ticker}.", reply_to_message_id=message.id)
            return
        enviada = bot.send_message(message.chat.id, f"Buscando...")
        doc_reg = buscar_ultimo_regulamento(buscar_cnpj(ticker))
        if doc_reg:
            doc_reg["codigoFII"] = ticker
            env2(doc_reg, [message.from_user.id]) 
        else:
            bot.send_message(message.chat.id, f'Não encontramos informações sobre regulamento publicado por este fundo.', reply_to_message_id=message.id)    
        bot.delete_message(message.chat.id, enviada.id)
    elif len(message.text.strip().split()) == 1:
        bot.send_message(message.chat.id, f'Informe o código de negociação do fundo que você deseja ver o último regulamento publicado.\nEx.: "/reg CYCR11".', reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Uso incorreto. Para ver o último regulamento publicado por um fundo, envie /reg CODIGO_FUNDO.\nEx.: "/reg CYCR11".', reply_to_message_id=message.id)

@bot.message_handler(commands=["fnet"])
def handle_command(message):
    #cmd = message.text.split()[0]
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        if not ticker in base.colunas():
            if ticker in tokens_infra.keys():#("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                #bot.send_message(message.chat.id, f"https://www.b3.com.br/pt_br/produtos-e-servicos/negociacao/renda-variavel/fundos-de-investimentos/fi-infra/fi-infra-listados/", reply_to_message_id=message.id)
                msg = f"https://sistemaswebb3-listados.b3.com.br/fundsPage/main/38065012000177/{ticker[:4]}/27/previousCommunications"
                bot.send_message(message.chat.id, msg, reply_to_message_id=message.id)
                return
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo {ticker}.", reply_to_message_id=message.id)
            return
        msg = f"https://fnet.bmfbovespa.com.br/fnet/publico/abrirGerenciadorDocumentosCVM?cnpjFundo={buscar_cnpj(ticker)}"
        bot.send_message(message.chat.id, msg, reply_to_message_id=message.id) 
    elif len(message.text.strip().split()) == 1:
        bot.send_message(message.chat.id, f'Informe o código do fundo.\nEx.: "/reg CYCR11".', reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Uso incorreto. Para aproveitar essa função, envie /fnet CODIGO_FUNDO.\nEx.: "/fnet CYCR11".', reply_to_message_id=message.id)
            
@bot.message_handler(commands=["docs", "ultimos_documentos"])
def handle_command(message):
    cmd = message.text.split()[0]
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        if not ticker in base.colunas():
            if ticker in tokens_infra.keys():#("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                #bot.send_message(message.chat.id, f"Desculpe, mas no momento não temos a opção ver de documentos de FI-Infras.", reply_to_message_id=message.id)
                enviada = bot.send_message(message.chat.id, f"Buscando documentos...")
                documentos = buscar_documentos_infra(tokens_infra[ticker], agora()-datetime.timedelta(days=30))
                #print(documentos)
                if len(documentos) == 0:
                    bot.send_message(message.chat.id, f"O FII-Infra imobiliário {ticker} não disponibilizaou nenhum documento nos últimos 30 dias.")
                    return
                for doc in documentos:
                    print(ticker, "-", doc["name"])
                    #doc["codigoFII"] = ticker
                    env_infra(ticker, doc, [message.from_user.id])
                bot.delete_message(message.chat.id, enviada.id)
                return
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo listado {ticker}.", reply_to_message_id=message.id)
            return
        enviada = bot.send_message(message.chat.id, f"Buscando documentos...")
        documentos = buscar_documentos2(buscar_cnpj(ticker), datetime.datetime.now() - datetime.timedelta(days=30))
        #print(documentos)
        if len(documentos) == 0:
            bot.send_message(message.chat.id, f"O fundo {ticker} não disponibilizaou nenhum documento nos últimos 30 dias.")
            return
        for doc in documentos:
            print(ticker, "-", doc["tipoDocumento"])
            doc["codigoFII"] = ticker
            env(doc, message.from_user.id)
        bot.delete_message(message.chat.id, enviada.id)
            #if doc["tipoDocumento"] == "Rendimentos e Amortizações":
                #informar_proventos(doc, message.from_user.id)
    elif len(message.text.strip().split()) == 1:
        bot.send_message(message.chat.id, f'Informe o código de negociação do fundo que você deseja ver os últimos documentos.\nEx.: "{cmd} URPR11".', reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Uso incorreto. Para receber os comunicados mais recentes de um fundo, envie {cmd} CODIGO_FUNDO.\nEx.: "{cmd} URPR11".', reply_to_message_id=message.id)

@bot.message_handler(commands=["seguir"])
def handle_command(message):
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        r = base.inserir(ticker, str(message.chat.id))
        if r == 0:
            bot.send_message(message.chat.id, f"Parabéns! Agora você receberá todos os documentos e comunicados referentes ao fundo {ticker}.", reply_to_message_id=message.id)
        elif r == 1:
            bot.send_message(message.chat.id, "Você já segue esse fundo. Assim que forem divulgados novos documentos ou comunicados, lhe enviaremos.", reply_to_message_id=message.id)
        elif r == -1:
            if ticker in base_infra.colunas():
                #bot.send_message(message.chat.id, f"Desculpe, mas no momento não temos a opção de seguir FI-Infras.", reply_to_message_id=message.id)
                r = base_infra.inserir(ticker, str(message.chat.id))
                if r == 0:
                    bot.send_message(message.chat.id, f"Parabéns! Agora você receberá todos os documentos e comunicados referentes ao fundo {ticker}.", reply_to_message_id=message.id)
                elif r == 1:
                    bot.send_message(message.chat.id, "Você já segue esse fundo. Assim que forem divulgados novos documentos ou comunicados, lhe enviaremos.", reply_to_message_id=message.id)
            else:
                bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo {ticker}.", reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, 'Uso incorreto. Para seguir um fundo envie /seguir CODIGO_FUNDO. Ex.: "/seguir URPR11"', reply_to_message_id=message.id)
        
@bot.message_handler(commands=["desinscrever"])
def handle_command(message):
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.split()) != 2:
        bot.send_message(message.chat.id, 'Uso incorreto. Para deixar de seguir um fundo envie /desinscrever CODIGO_FUNDO. Ex.: "/desinscrever URPR11"', reply_to_message_id=message.id)
        return
    ticker = message.text.split()[1].strip().upper()
    r = base.remover(ticker, str(message.from_user.id))
    if r == 0:
        bot.send_message(message.chat.id, f"Pronto! Você não receberá mais informações sobre o fundo {ticker}.", reply_to_message_id=message.id)
    elif r == 1:
        bot.send_message(message.chat.id, f'Você ainda não segue esse fundo. Para seguir envie: "/seguir {ticker}"', reply_to_message_id=message.id)
    elif r == -1:
        r = base_infra.remover(ticker, str(message.from_user.id))
        if r == 0:
            bot.send_message(message.chat.id, f"Pronto! Você não receberá mais informações sobre o fundo {ticker}.", reply_to_message_id=message.id)
        elif r == 1:
            bot.send_message(message.chat.id, f'Você ainda não segue esse fundo. Para seguir envie: "/seguir {ticker}"', reply_to_message_id=message.id)
        elif r == -1:
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo {ticker}.", reply_to_message_id=message.id)
        
@bot.message_handler(commands=["fundos_seguidos"])
def handle_command(message):
    #print(message)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(message.from_user.first_name, message.text)
    fs = base.buscar_seguidos(str(message.from_user.id))
    fs.extend(base_infra.buscar_seguidos(str(message.from_user.id)))
    fs.sort()
    if len(fs) == 0:
        bot.send_message(message.chat.id, f"Você ainda não está seguindo nenhum fundo. Para começar, utilize o comando /seguir", reply_to_message_id=message.id)
    else:
        resposta = "Fundos que você segue:"
        for f in fs:
            resposta += "\n"+f
        bot.send_message(message.chat.id, resposta, reply_to_message_id=message.id)
       
       
def get_ticker_value(ticker):
    if ticker.upper() == "KNHF11":
        raise Exception("Não encontrado")
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'} 
    url = f'https://www.google.com/search?q={ticker}'
    try:
        res = requests.get(url, headers=headers)
        html_page = res.text
        
        #if "BVMF:"+ticker.upper() not in html_page:
            #raise Exception("Não encontrado")

        
        soup = BeautifulSoup(html_page, 'html.parser')

        #print(soup.find_all('span'))

        valor = float(soup.find_all('span', {"class":'IsqQVc NprOob wT3VGc'})[0].text.replace(",","."))
    except:
        time.sleep(2)
        res = requests.get(url, headers=headers)
        html_page = res.text
        
        #if "BVMF:"+ticker.upper() not in html_page:
            #raise Exception("Não encontrado")

        
        soup = BeautifulSoup(html_page, 'html.parser')

        #print(soup.find_all('span'))

        valor = float(soup.find_all('span', {"class":'IsqQVc NprOob wT3VGc'})[0].text.replace(",","."))
        
    return valor
    
def get_variacao(ticker):
    valor = ""
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'} 
    url = f'https://www.google.com/search?q={ticker}'
    try:
        res = requests.get(url, headers=headers)
        html_page = res.text       
        soup = BeautifulSoup(html_page, 'html.parser')
        sinal = soup.find_all('span', {"jsname":'qRSVye'})[0].text.strip()[0]
        valor = soup.find_all('span', {"class":'jBBUv'})[0].text.strip().replace(".",",").replace("(","").replace(")","").replace("%","")
        if sinal == "+":
            valor = "+"+valor
        elif sinal in ("−","-"):
            valor = "-"+valor
    except:
        try:
            res = requests.get(url, headers=headers)
            html_page = res.text       
            soup = BeautifulSoup(html_page, 'html.parser')
            sinal = soup.find_all('span', {"jsname":'qRSVye'})[0].text.strip()[0]
            valor = soup.find_all('span', {"class":'jBBUv'})[0].text.strip().replace(".",",").replace("(","").replace(")","").replace("%","")
            if sinal == "+":
                valor = "+"+valor
            elif sinal in ("−","-"):
                valor = "-"+valor
        except:
            pass
    
    return valor

proxies = {'http': 'http://200.187.70.223:3128',
'https': 'http://200.187.70.223:3128'
}
def get_ticker_variacao2(ticker):
    valor = None
    variacao = ""
    if ticker.upper() == "KNHF11":
        return (valor, variacao)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'} 
    
    url = "https://statusinvest.com.br/fundos-imobiliarios/" + ticker
    try:

        res = requests.get(url, headers=headers, proxies=proxies, verify=False)
        html_page = res.text       
        soup = BeautifulSoup(html_page, 'html.parser')
        #print(soup.prettify())
        valor = soup.select_one('.special strong').text.strip()
        variacao = soup.select_one('.special b').text.strip();
        if len(variacao) > 0 and not variacao.startswith("-") and variacao != "0,00%":
            variacao = "+" + variacao
    except:
        #traceback.print_exc()
        time.sleep(5)
        try:
        #    proxies = {'http': 'http://200.187.70.223:3128',
        #'https': 'http://200.187.70.223:3128'
        #}
            res = requests.get(url, headers=headers,proxies=proxies,verify=False)
            html_page = res.text       
            soup = BeautifulSoup(html_page, 'html.parser')
            valor = soup.select_one('.special strong').text.strip()
            variacao = soup.select_one('.special b').text.strip()
            if len(variacao) > 0 and not variacao.startswith("-") and variacao != "0,00%":
                variacao = "+" + variacao
        except:
            pass
    
    return (valor, variacao)
    
def get_ticker_variacao3(ticker):
    valor = None
    variacao = ""
    #if ticker.upper() == "KNHF11":
        #return (valor, variacao)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'} 
    
    url = f"https://finance.yahoo.com/quote/{ticker}.SA/"
    try:

        res = requests.get(url, headers=headers)
        html_page = res.text       
        soup = BeautifulSoup(html_page, 'html.parser')
        #print(soup.prettify())
        valor = soup.select_one(f'[data-field="regularMarketPrice"][data-symbol="{ticker}.SA"]').text.strip().replace(".",",").replace("(","").replace(")","")
        variacao = soup.select_one(f'[data-field="regularMarketChangePercent"][data-symbol="{ticker}.SA"]').text.strip().replace(".",",").replace("(","").replace(")","")
        #if len(variacao) > 0 and not variacao.startswith("-") and variacao != "0,00%":
            #variacao = "+" + variacao
    except:
        #traceback.print_exc()
        time.sleep(5)
        try:
        #    proxies = {'http': 'http://200.187.70.223:3128',
        #'https': 'http://200.187.70.223:3128'
        #}
            #res = requests.get(url, headers=headers,proxies=proxies,verify=False)
            res = requests.get(url, headers=headers)
            html_page = res.text       
            soup = BeautifulSoup(html_page, 'html.parser')
            valor = soup.select_one(f'[data-field="regularMarketPrice"][data-symbol="{ticker}.SA"]').text.strip().replace(".",",").replace("(","").replace(")","")
            variacao = soup.select_one(f'[data-field="regularMarketChangePercent"][data-symbol="{ticker}.SA"]').text.strip().replace(".",",").replace("(","").replace(")","")
            #if len(variacao) > 0 and not variacao.startswith("-") and variacao != "0,00%":
                #variacao = "+" + variacao
        except:
            pass
    
    return (valor, variacao)
    
def get_ticker_value(ticker):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'} 
    ticker = ticker.upper()
    url = f"https://finance.yahoo.com/quote/{ticker}.SA/"
    try:
        res = requests.get(url, headers=headers)
        html_page = res.text       
        soup = BeautifulSoup(html_page, 'html.parser')
        print(soup.select_one(f'[data-field="regularMarketPrice"][data-symbol="{ticker}.SA"]').text.strip().replace(",",".").replace("(","").replace(")",""))
        valor = float(",".join(soup.select_one(f'[data-field="regularMarketPrice"][data-symbol="{ticker}.SA"]').text.strip().replace("(","").replace(")","").rsplit(",",1)).replace(",",""))
    except:
        traceback.print_exc()
        time.sleep(2)
        res = requests.get(url, headers=headers)
        html_page = res.text       
        soup = BeautifulSoup(html_page, 'html.parser')
        valor = float(",".join(soup.select_one(f'[data-field="regularMarketPrice"][data-symbol="{ticker}.SA"]').text.strip().replace("(","").replace(")","").rsplit(",",1)).replace(",",""))
    
    return valor
    
def get_ticker_variacao(ticker):
    valor = None
    variacao = ""
    if ticker.upper() == "KNHF11":
        return (valor, variacao)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'} 
    url = f'https://www.google.com/search?q={ticker}'
    try:
        res = requests.get(url, headers=headers)
        html_page = res.text       
        soup = BeautifulSoup(html_page, 'html.parser')
        valor = float(soup.find_all('span', {"class":'IsqQVc NprOob wT3VGc'})[0].text.replace(",","."))
        sinal = soup.find_all('span', {"jsname":'qRSVye'})[0].text.strip()[0]
        variacao = soup.find_all('span', {"class":'jBBUv'})[0].text.strip().replace(".",",").replace("(","").replace(")","").replace("%","")
        if sinal == "+":
            variacao = "+"+variacao
        elif sinal in ("−","-"):
            variacao = "-"+variacao
    except:
        try:
            res = requests.get(url, headers=headers)
            html_page = res.text       
            soup = BeautifulSoup(html_page, 'html.parser')
            if not valor:
                valor = float(soup.find_all('span', {"class":'IsqQVc NprOob wT3VGc'})[0].text.replace(",","."))
            sinal = soup.find_all('span', {"jsname":'qRSVye'})[0].text.strip()[0]
            variacao = soup.find_all('span', {"class":'jBBUv'})[0].text.strip().replace(".",",").replace("(","").replace(")","").replace("%","")
            if sinal == "+":
                variacao = "+"+variacao
            elif sinal in ("−","-"):
                variacao = "-"+variacao
        except:
            pass
    
    return (valor, variacao)
       
        
#@bot.message_handler(regexp=r"(\s)*/cotacao.* [A-Za-z]{4}11")
@bot.message_handler(commands=["cotacao"])
def handle_command(message):
    try:
        print(agora(), message.from_user.first_name, message.text)
        ticker = message.text.split()[1].strip()
        enviada = bot.send_message(message.chat.id, "Buscando...", reply_to_message_id=message.id)
        valor = get_ticker_value(ticker)
        bot.delete_message(message.chat.id, enviada.id)
        bot.send_message(message.chat.id, f"R$ {valor:.2f}".replace(".",","), reply_to_message_id=message.id)
    except:
        bot.send_message(message.chat.id, 'Ocorreu um erro, tente novamente.')
        
@bot.message_handler(commands=["cnpj"])
def handle_command(message):
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        try:
            ticker = message.text.split()[1].strip().upper()
            if ticker in tokens_infra.keys():#("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                bot.send_message(message.chat.id, f"Desculpe, mas no momento esta função não está disponível para FI-Infras.", reply_to_message_id=message.id)
                return
            cnpj = buscar_cnpj(ticker)
            bot.send_message(message.chat.id, cnpj, reply_to_message_id=message.id)
        except:
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo {ticker}.")
    else:
        bot.send_message(message.chat.id, 'Uso incorreto. Para ver o CNPJ um fundo envie /cnpj CODIGO_FUNDO. Ex.: "/cnpj URPR11"', reply_to_message_id=message.id)

def mensagem_instrucoes(comandos=comandos):
    msg = ""
    for comando, descricao in comandos:
        msg += f"/{comando}: {descricao}\n\n"
    return msg

@bot.message_handler(commands=["start"])
def handle_command(message):
    #print(message)
    #bot.forward_message("-743953207", message.chat.id, message.id)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    bot.send_message("-743953207", f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Seja bem-vindo ao @SuperFIIsBot!!!\n\n")
    bot.send_message(message.from_user.id, "Segue a lista de comandos disponíveis e suas respectivas descrições:\n\n"+mensagem_instrucoes())
    bot.send_message(message.from_user.id, "Em caso de dúvidas ou sugestões, entre em contato diretamente com o desenvolvedor @gilmartaj, ficaremos felizes em ajudar!")
    
@bot.message_handler(commands=["mais"])
def handle_command(message):
    #print(message)
    #bot.forward_message("-743953207", message.chat.id, message.id)
    #bot.send_message("-743953207", f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Segue a lista de comandos extra que o bot disponibiliza:\n\n"+mensagem_instrucoes(mais_comandos))
    bot.send_message(message.from_user.id, "Em caso de dúvidas ou sugestões, entre em contato diretamente com o desenvolvedor @gilmartaj, ficaremos felizes em ajudar!")
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    
@bot.message_handler(commands=["ajuda"])
def handle_command(message):
    #print(message)
    print(agora(), message.from_user.first_name, message.text)
    bot.send_message(message.from_user.id, "Segue a lista de comandos disponíveis e suas respectivas descrições:\n\n"+mensagem_instrucoes()+"\nEm caso de dúvidas ou sugestões, entre em contato diretamente com o desenvolvedor @gilmartaj", reply_to_message_id=message.id)
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    
@bot.message_handler(commands=["doacao"])
def handle_command(message):
    print(agora(), message.from_user.first_name, message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Além do tempo de desenvolvimento, manter o bot rodando exige um servidor, e isso tem um custo. Se o bot é útil para você e não lhe fazem falta alguns centavos, ajude o projeto doando a partir de 1 centavo para a Chave Pix de e-mail do desenvolvedor: gil77891@gmail.com\n\nObs.: Não use este e-mail para contato, isto pode ser feito aqui mesmo pelo Telegram, enviando uma mensagem para @gilmartaj.")
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    
@bot.message_handler(commands=["contato"])
def handle_command(message):
    print(agora(), message.from_user.first_name, message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Para dúvidas, sugestões e reportes de erros, envie uma mensagem direta para o desenvolvedor @gilmartaj, aqui mesmo pelo Telegram.")
    log(f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    
@bot.message_handler(commands=["infprv"])
def handle_command(message):
    print(agora(), message.from_user.first_name, message.from_user.id, message.text)
    if str(message.from_user.id) == "556068392":
        parts = message.text.split()
        if parts[1] not in base_infra.colunas():
            bot.send_message(message.from_user.id, "Fundo inválido!", reply_to_message_id=message.id)
            return
        if len(parts) != 5:
            bot.send_message(message.from_user.id, "Parâmetros inválidos!", reply_to_message_id=message.id)
            return
        try:
            informar_provento_infra(parts[1], parts[2].replace(",","."), parts[3], parts[4])
        except:
            bot.send_message(message.from_user.id, "Aconteceu algum erro...", reply_to_message_id=message.id)
            return
        bot.send_message(message.from_user.id, "Pronto!", reply_to_message_id=message.id)
            

def thread_envio(doc, seguidores):
    #print("Enviando...",seguidores)
    try:
        try:
            #for seg in seguidores:
                #seg = int(seg)
                try:
                    env2(doc, seguidores)
                except:
                    print("ERRO",doc["tipoDocumento"])
                    traceback.print_exc()
                    
        except:
            ultima_busca[f] = h
            traceback.print_exc()
        if doc["tipoDocumento"] == "Rendimentos e Amortizações":
            #for seg in seguidores:
                #seg = int(seg)
           informar_proventos(doc, seguidores)
        elif "Informe Mensal Estruturado" in doc["tipoDocumento"]:
            informar_atualizacao_patrimonial(doc, seguidores)
    except:
        traceback.print_exc()

vlock = threading.Lock()

def verificar():
    global sheet
    global base
    global vlock
    global fila_doc
    try:
        bot.send_message("-1001527968438", "Verificando...")
    except:
        pass
    """try:
        vlocked = vlock.acquire(timeout=2)
        if not vlocked:
            return
    except:
        return"""
    with vlock:
        try:
            sheet_aux = client.open("SeguidoresFIIs").sheet1
            base_aux = BaseCache(sheet)
            if base_aux:
                base = base_aux
                time.sleep(30)
        except:
            pass
        print("Verificando...")
        for f in base.colunas():
            print(f)
            seguidores = base.buscar_seguidores(f)
            if len(seguidores) > 0:
                #print(f, len(seguidores))
                h = ultima_busca[f]
                #ultima_busca[f] = agora()
                documentos = []
                try:
                    documentos = buscar_documentos(buscar_cnpj(f), h)
                    for doc in documentos:
                        try:
                            sfnot.notificar_seguidores_documento_fundo_bot(f, doc)
                        except:
                            pass
                        if doc not in fila_doc.queue:
                            fila_doc.put(doc)
                    #print(len(documentos))
                except:
                    traceback.print_exc()
                #if len(documentos) == 0:
                 #   for seg in seguidores:
                 #       seg = int(seg)
                        #bot.send_message(seg, f + " - Nenhum documento")
                #with concurrent.futures.ThreadPoolExecutor(max_workers = 5) as executor:
                #with ThreadPool(processes = 5) as executor:
                while not fila_doc.empty():
                    try:
                        doc = fila_doc.get(block=False)
                        print(f, "-", doc["tipoDocumento"])
                        doc["codigoFII"] = f
                        thread_envio(doc, seguidores)                
                        de = doc["dataEntrega"]
                        ultima_busca[f] = datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13]), minute=int(de[14:16]), tzinfo=tz_info)
                    except:
                        pass#ultima_busca[f] = agora()
                        #Thread(target=thread_envio, args=(doc, seguidores), daemon=True).start()
                        #executor.submit(thread_envio, doc, seguidores)
                        #try:
                            #executor.apply_async(thread_envio, args=(doc, seguidores))
                        #except:
                            #traceback.print_exc()
        """try:
            vlock.release()
        except:
            pass"""               
def verificar2():
    for f in base.colunas():
        seguidores = base.buscar_seguidores(f)
        if len(seguidores) > 0:
            #print(f, len(seguidores))
            h = ultima_busca[f]
            ultima_busca[f] = agora()
            documentos = []
            try:
                documentos = buscar_documentos(buscar_cnpj(f), h)
            except:
                pass
            
            #if len(documentos) == 0:
             #   for seg in seguidores:
             #       seg = int(seg)
                    #bot.send_message(seg, f + " - Nenhum documento")
            
            for doc in documentos:
                print(f, "-", doc["tipoDocumento"])
                
                doc["codigoFII"] = f
                try:
                    env(doc, seguidores)
                    if doc["tipoDocumento"] == "Rendimentos e Amortizações":
                        informar_proventos(doc, [seguidores])
                    elif "Informe Mensal Estruturado" in doc["tipoDocumento"]:
                        informar_atualizacao_patrimonial(doc, seg)
                except:
                    ultima_busca[f] = h
                    
def agora():
    #return datetime.datetime.utcnow().astimezone(pytz.timezone("America/Bahia"))
    return datetime.datetime.now(tz=pytz.timezone("America/Bahia"))
    
def exec_ver(parada):
    try:
        espera = parada - agora()
        print(espera.total_seconds())
        time.sleep(espera.total_seconds())
        Thread(target=verificar, daemon=True).start()
    except:
        pass
        
def verificacao_periodica():
    #h = agora()
    #exec_ver(datetime.datetime(h.year, h.month, h.day, 22, 30, tzinfo=tz_info))

    while True:
        try:
            print(f"init {agora()}")
            #bot.send_message("-743953207", str(agora()))
            Thread(target=verificar, daemon=False).start()
            #verificar()
            h = agora()
            if is_dia_util(h.date()) and h.hour > 7 and h.hour < 22:
                time.sleep(600)
            else:
                time.sleep(3600)
                print("Verificando...")
        except:
            time.sleep(10)
            pass
          
        
        """parada = agora() + datetime.timedelta(seconds = 5)
        #parada = datetime.datetime(h.year, h.month, h.day, 20, 58, tzinfo=h.tzinfo)
        print(h, parada)
        espera = parada - h
        print(espera.total_seconds())
        time.sleep(espera.total_seconds())
        verificar()"""
        """if h.hour > datetime.datetime(h.year, h.month, h.day, 21, 30, tzinfo=tz_info) or h.hour < datetime.datetime(h.year, h.month, h.day, 9, 30, tzinfo=tz_info):"""
        #if h.hour > datetime.datetime(h.year, h.month, h.day, 21, 30, tzinfo=tz_info):
        
        #exec_ver(datetime.datetime(h.year, h.month, h.day, 20, 40, tzinfo=tz_info))        

def is_feriado(data):
    return (data.day == 1 and data.month == 1 or data.day == 21 and data.month == 4 or data.day == 1 and data.month == 5 or data.day == 1 and data.month == 5 or data.day == 7 and data.month == 9 or data.day == 12 and data.month == 10 or data.day == 2 and data.month == 11 or data.day == 15 and data.month == 11 or data.day == 25 and data.month == 12)
    
def is_feriado_movel(data):
    return data in (datetime.date(2023,4,7),datetime.date(2023,6,8),datetime.date(2023,12,29))
    
def is_fim_de_semana(data):
    return data.weekday() in (5,6)

def is_dia_util(data):       
    return not is_fim_de_semana(data) and not is_feriado(data) and not is_feriado_movel(data)
    
def thread_fechamento():
    h = agora()
    parada = datetime.datetime(h.year, h.month, h.day, 20, 0, tzinfo=h.tzinfo)
    if h.hour >= 20:
        parada += datetime.timedelta(days=1)
        
    #parada = agora() + datetime.timedelta(seconds=10)
    #print("Esperando")
    
    while True:
        espera = parada - agora()
        print("Esperando...")
        time.sleep(espera.total_seconds())
        try:
            if is_dia_util(agora().date()):
                Thread(target=informar_fechamento2, daemon=True).start()
        except:
            pass
        parada += datetime.timedelta(days=1)

def convv(v):
    if v >= 1000000000:
        return f"R$ {round(v // 10000000 / 100, 2)} bi".replace(".", ",")
    elif v >= 10000000:
        return f"R$ {round(v // 100000 / 10, 1)} M".replace(".", ",")
    elif v >= 1000000:
        return f"R$ {round(v // 10000 / 100, 2)} M".replace(".", ",")
    elif v >= 10000:
        return f"R$ {round(v // 100 / 10, 1)} mil".replace(".", ",")
    else:
        return f"R$ {round(v, 2):.2f} ".replace(".", ",")
        
def thread_teste():
    docs = buscar_documentos(buscar_cnpj("CCME11"), desde=agora()-datetime.timedelta(days=30))  
    print(len(docs))
    for doc in docs:
        print(doc["tipoDocumento"])
        doc["codigoFII"] = "CCME11"
        env2(doc, ["-495713843", "556068395","-743953207", "556068392"])
        
tz_info = agora().tzinfo
      
ultima_busca = {}
for f in base.colunas():
    ultima_busca[f] = agora() - datetime.timedelta(minutes=750)
    
ultima_busca_infra = {}
for f in base_infra.colunas():
    ultima_busca_infra[f] = agora() - datetime.timedelta(minutes=750)
    
def verificar_infra():
    global sheet_infra
    global base_infra
    try:
        bot.send_message("-1001527968438", "Verificando Infra...")
    except:
        pass
    try:
        sheet_infra = client.open("SeguidoresFI-Infras").sheet1
        base_infra = BaseCache(sheet_infra)
    except:
        pass
    #print("Verificando...")
    for f in base_infra.colunas():
        seguidores = base_infra.buscar_seguidores(f)
        if len(seguidores) > 0:
            #print(f, len(seguidores))
            h = ultima_busca_infra[f]
            #ultima_busca_infra[f] = agora()
            documentos = []
            try:
                documentos = buscar_documentos_infra(tokens_infra[f], h)
            except:
                pass
            
            for doc in documentos:
                try:
                    print(f,doc)
                    env_infra(f, doc, seguidores)
                    #env_infra(f, doc, seguidores)
                    de = doc["date"]
                    ultima_busca_infra[f] = datetime.datetime(year=int(de[0:4]), month=int(de[5:7]), day=int(de[8:10]), hour=int(de[11:13]), minute=int(de[14:16]), tzinfo=tz_info)
                except:
                    ultima_busca_infra[f] = h
            try:
                prov = buscar_ultimo_provento_infra(f)
                #nova_data = datetime.datetime.strptime(list(prov.values())[0], "%d/%m/%Y") if prov != None else datetime.datetime.min
                #ultima_data = datetime.datetime.strptime(list(ultimo_provento_infra[f].values())[0], "%d/%m/%Y") if ultimo_provento_infra[f] != None else datetime.datetime.min
                #if prov != ultimo_provento_infra[f] and nova_data >= ultima_data:
                #if prov != ultimo_provento_infra[f]:
                if not comparar_proventos_infra(ultimo_provento_infra[f], prov):
                    print(log(f"Provento encontrado: {f}"))
                    informar_provento_infra1(prov, seguidores)
                    ultimo_provento_infra[f] = prov
            except:
                traceback.print_exc()
            time.sleep(2)
                    

def verificacao_periodica_infra():

    for f in base_infra.colunas():
        try:
            print(f"Atualizando rendimento {f}...")
            ultimo_provento_infra[f] = buscar_ultimo_provento_infra(f)
        except:
            try:
                time.sleep(5)
                ultimo_provento_infra[f] = buscar_ultimo_provento_infra(f)
            except:
                traceback.print_exc()
        time.sleep(2)

    time.sleep(600)

    while True:
        try:
            Thread(target=verificar_infra, daemon=True).start()
            h = agora()
            if is_dia_util(h.date()) and h.hour > 6 and h.hour < 23:
                time.sleep(600)
            else:
                time.sleep(10800)
            print("Verificando infra...", agora())
        except:
            pass
   
tokens_infra = {
    "BDIF11": "eyJpZGVudGlmaWVyRnVuZCI6IkJESUYiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "BIDB11": "eyJpZGVudGlmaWVyRnVuZCI6IkJJREIiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "BODB11": "eyJpZGVudGlmaWVyRnVuZCI6IkJPREIiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "CDII11": "eyJpZGVudGlmaWVyRnVuZCI6IkNESUkiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "CPTI11": "eyJpZGVudGlmaWVyRnVuZCI6IkNQVEkiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "IFRA11": "eyJpZGVudGlmaWVyRnVuZCI6IklGUkEiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "JURO11": "eyJpZGVudGlmaWVyRnVuZCI6IkpVUk8iLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "KDIF11": "eyJpZGVudGlmaWVyRnVuZCI6IktESUYiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "NUIF11": "eyJ0eXBlRnVuZCI6MjcsImNucGoiOiI0MDk2MzQwMzAwMDE1MCIsImlkZW50aWZpZXJGdW5kIjoiTlVJRiJ9",
    "OGIN11": "eyJpZGVudGlmaWVyRnVuZCI6Ik9HSU4iLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "RBIF11": "eyJpZGVudGlmaWVyRnVuZCI6IlJCSUYiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "SNID11": "eyJpZGVudGlmaWVyRnVuZCI6IlNOSUQiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "XPID11": "eyJpZGVudGlmaWVyRnVuZCI6IlhQSUQiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    #FIPS
    "AATH11": "eyJpZGVudGlmaWVyRnVuZCI6IkFBVEgiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "AZIN11": "eyJpZGVudGlmaWVyRnVuZCI6IkFaSU4iLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "BRZP11": "eyJpZGVudGlmaWVyRnVuZCI6IkJSWlAiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "BDIV11": "eyJpZGVudGlmaWVyRnVuZCI6IkJESVYiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "ENDD11": "eyJpZGVudGlmaWVyRnVuZCI6IkVOREQiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "ESUD11": "eyJpZGVudGlmaWVyRnVuZCI6IkVTVUQiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "ESUT11": "eyJpZGVudGlmaWVyRnVuZCI6IkVTVVQiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "ESUU11": "eyJpZGVudGlmaWVyRnVuZCI6IkVTVVUiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "FPOR11": "eyJpZGVudGlmaWVyRnVuZCI6IkZQT1IiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "KNOX11": "eyJpZGVudGlmaWVyRnVuZCI6IktOT1giLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "NVRP11": "eyJpZGVudGlmaWVyRnVuZCI6Ik5WUlAiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "OPEQ11": "eyJpZGVudGlmaWVyRnVuZCI6Ik9QRVEiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "OPHF11": "eyJpZGVudGlmaWVyRnVuZCI6Ik9QSEYiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "PFIN11": "eyJpZGVudGlmaWVyRnVuZCI6IlBGSU4iLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "PICE11": "eyJpZGVudGlmaWVyRnVuZCI6IlBJQ0UiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "PPEI11": "eyJpZGVudGlmaWVyRnVuZCI6IlBQRUkiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "VIGT11": "eyJpZGVudGlmaWVyRnVuZCI6IlZJR1QiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "XPIE11": "eyJpZGVudGlmaWVyRnVuZCI6IlhQSUUiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
}

ultimo_provento_infra = {}

       
print("Robô iniciado.")
#print(fiis_cnpj)

def informar_atualizacao_patrimonial(doc, usuarios):
#422748
    r = requests.get(f'https://fnet.bmfbovespa.com.br/fnet/publico/downloadDocumento?id={doc["id"]}', headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"})

    v_atual = 0

    try:
        v_atual = get_ticker_value(doc["codigoFII"])
    except:
        pass

    dados = xmltodict.parse(r.content)

    mensagem = "Atualização patrimonial:"
    #mensagem += f'FII: {doc["codigoFII"]}'
    mensagem += f'\n\n\U0001F3E0Código: {doc["codigoFII"]}'
    
    competencia = dados["DadosEconomicoFinanceiros"]["DadosGerais"]["Competencia"]
    if re.match(r"^\d{4}-\d{2}-\d{2}$",competencia):
        competencia = competencia[5:7]+"/"+competencia[0:4]
        
    mensagem += f"\n\U0001F5D3Competência: {competencia}\n"
    
    d = dados["DadosEconomicoFinanceiros"]["InformeMensal"]["Resumo"]
    #print(d)
    pl = float(d["PatrimonioLiquido"])
    valz = round(float(d["RentEfetivaMensal"]["RentPatrimonialMes"])*100,5)
    vp = float(d["ValorPatrCotas"])
    pvp = round(v_atual/vp,2)
    
    ativo = float(d["Ativo"])
    d = dados["DadosEconomicoFinanceiros"]["InformeMensal"]["InformacoesPassivo"]
    dividas = 0.00
    try:
        dividas += float(d["ObrigacoesAquisicaoImov"])
    except:
        pass
    try:
        dividas += float(d["ObrigacoesSecRecebiveis"])
    except:
        pass
    try:
        dividas += float(d["OutrosValoresPagar"])
    except:
        pass
    alavancagem = dividas/ativo
    
    mensagem += f'\n\U0001F4CAPat. líquido: {convv(pl)}'
    
    if valz > 0:
        valz = f"+{valz}%".replace(".",",")
        mensagem += f'\n\U0001F4C8Variação: {valz}'
    elif valz < 0:
        valz = f"{valz}%".replace(".",",")
        mensagem += f'\n\U0001F4C9Variação: {valz}'
    else:
        valz = f"0,00%"
        mensagem += f'\n\U0001F4C9Variação: {valz}'
        
    vp = f'R$ {round(vp*100//1/100,2):.2f}'.replace(".",",")
    
    pvp = f"{pvp:.2f}".replace(".",",")
    
    mensagem += f'\n\U0001F4B5VP/cota: {vp}'
    if v_atual:
        mensagem += f'\n\u2797P/VP atual: {pvp}'
    mensagem += f'\n\u26A0Alavancagem: {alavancagem:.2%}'.replace(".",",")
        
    #print(mensagem)
    
    #print(convv(pl))
    #print(valz)
    #print(vp)
    #print(pvp)
        
    mensagem += "\n\n@RepositorioDeFIIs"
    for u in usuarios:
        bot.send_message(u, mensagem)
        
def buscar_cnpj_infra(fundo):
    return buscar_info_b3_infra(fundo)["cnpj"]

def buscar_info_b3_infra(fundo):
    url = f'https://sistemaswebb3-listados.b3.com.br/fundsProxy/fundsCall/GetDetailFundSIG/{tokens_infra[fundo]}'
    r = requests.get(url)
    return r.json()["detailFund"]

def buscar_info_ambima_infra(fundo):
    url = f"https://data.anbima.com.br/fundos-bff/fundos?page=0&size=20&field=&order=&q={buscar_cnpj_infra(fundo)}"
    print(url)
    r = requests.get(url)
    print(r.json())
    return r.json()["content"][0]

def buscar_patrimonio_liquido_infra(fundo):
    return float(buscar_info_ambima_infra(fundo)["patrimonio_liquido"])
    
def format_dt_ambima(data):
    return data[8:10] + "/" + data[5:7] + "/" + data[0:4]
    
def informar_atualizacao_patrimonial_infra(fundo, usuarios):
#422748
    
    v_atual = 0

    try:
        v_atual = get_ticker_value(fundo)
    except:
        pass

    info_b3 = buscar_info_b3_infra(fundo)
    info_ambima = buscar_info_ambima_infra(fundo)

    mensagem = "Informação patrimonial:"
    #mensagem += f'FII: {doc["codigoFII"]}'
    mensagem += f'\n\n\U0001F3E0Código: {fundo}'
    
    competencia = info_ambima["data_referencia"]
    if re.match(r"^\d{4}/\d{2}/\d{2}$",competencia):
        competencia = format_dt_ambima(competencia)
        
    mensagem += f"\n\U0001F5D3Data ref.: {competencia}\n"
    
    #print(d)
    pl = float(info_ambima["patrimonio_liquido"])
    #valz = round(float(d["RentEfetivaMensal"]["RentPatrimonialMes"])*100,5)
    qt_cotas = int(info_b3["quotaCount"])
    vp = pl/qt_cotas
    pvp = round(v_atual/vp,2)
    
    mensagem += f'\n\U0001F4CAPat. líquido: {convv(pl)}'
    
    """if valz > 0:
        valz = f"+{valz}%".replace(".",",")
        mensagem += f'\n\U0001F4C8Variação: {valz}'
    elif valz < 0:
        valz = f"{valz}%".replace(".",",")
        mensagem += f'\n\U0001F4C9Variação: {valz}'
    else:
        valz = f"0,00%"
        mensagem += f'\n\U0001F4C9Variação: {valz}'"""
        
    vp = f'R$ {round(vp*100//1/100,2):.2f}'.replace(".",",")
    
    pvp = f"{pvp:.2f}".replace(".",",")
    
    mensagem += f'\n\U0001F4B5VP/cota: {vp}'
    if v_atual:
        mensagem += f'\n\u2797P/VP atual: {pvp}'
    #mensagem += f'\n\u26A0Alavancagem: {alavancagem:.2%}'.replace(".",",")
        
    #print(mensagem)
    
    #print(convv(pl))
    #print(valz)
    #print(vp)
    #print(pvp)
        
    mensagem += "\n\n@RepositorioDeFIIs"
    for u in usuarios:
        bot.send_message(u, mensagem)
        
def buscar_info_patrimonio_fip(cnpj):

    data = {"filtro":
     {
      "numeroRegistro": cnpj,
       "tipoRegistro":{"id":56}
     }
    }
    
    print("...")
    try:
        id_consulta = requests.post("https://web.cvm.gov.br/app/fundosweb/consultarFundo/getRegistrosPorFiltro", json=data, timeout=1.5).json()[0]["id"]
    except:
        try:
            id_consulta = requests.post("https://web.cvm.gov.br/app/fundosweb/consultarFundo/getRegistrosPorFiltro", json=data, timeout=3).json()[0]["id"]
        except:
            id_consulta = requests.post("https://web.cvm.gov.br/app/fundosweb/consultarFundo/getRegistrosPorFiltro", json=data, timeout=6).json()[0]["id"]
    print(id_consulta)

    try:
        id_registro = requests.get(f"http://web.cvm.gov.br/app/fundosweb/registrarFundo/getRegistroFundoPorIdParaConsulta/{id_consulta}", timeout=1.5).json()["registro"]["id"]
    except:
        try:
            id_registro = requests.get(f"http://web.cvm.gov.br/app/fundosweb/registrarFundo/getRegistroFundoPorIdParaConsulta/{id_consulta}", timeout=3).json()["registro"]["id"]
        except:
            id_registro = requests.get(f"http://web.cvm.gov.br/app/fundosweb/registrarFundo/getRegistroFundoPorIdParaConsulta/{id_consulta}", timeout=6).json()["registro"]["id"]
    print(id_registro)

    try:
        info_pat = requests.get(f"https://web.cvm.gov.br/app/fundosweb/patrimonioLiquido/getPatrimoniosLiquidos/{id_registro}", timeout=1.5).json()
    except:
        try:
            info_pat = requests.get(f"https://web.cvm.gov.br/app/fundosweb/patrimonioLiquido/getPatrimoniosLiquidos/{id_registro}", timeout=3).json()
        except:
            info_pat = requests.get(f"https://web.cvm.gov.br/app/fundosweb/patrimonioLiquido/getPatrimoniosLiquidos/{id_registro}", timeout=6).json()
    return info_pat
    
def buscar_info_patrimonio_infra(cnpj):

    data = {"filtro":
     {
      "numeroRegistro": cnpj
     }
    }
    
    print("...")
    try:
        id_consulta = requests.post("https://web.cvm.gov.br/app/fundosweb/consultarFundo/getRegistrosPorFiltro", json=data, timeout=1.5).json()[0]["id"]
    except:
        try:
            id_consulta = requests.post("https://web.cvm.gov.br/app/fundosweb/consultarFundo/getRegistrosPorFiltro", json=data, timeout=3).json()[0]["id"]
        except:
            id_consulta = requests.post("https://web.cvm.gov.br/app/fundosweb/consultarFundo/getRegistrosPorFiltro", json=data, timeout=6).json()[0]["id"]
    print(id_consulta)

    try:
        id_registro = requests.get(f"http://web.cvm.gov.br/app/fundosweb/registrarFundo/getRegistroFundoPorIdParaConsulta/{id_consulta}", timeout=1.5).json()["registro"]["id"]
    except:
        try:
            id_registro = requests.get(f"http://web.cvm.gov.br/app/fundosweb/registrarFundo/getRegistroFundoPorIdParaConsulta/{id_consulta}", timeout=3).json()["registro"]["id"]
        except:
            id_registro = requests.get(f"http://web.cvm.gov.br/app/fundosweb/registrarFundo/getRegistroFundoPorIdParaConsulta/{id_consulta}", timeout=6).json()["registro"]["id"]
    print(id_registro)

    try:
        info_pat = requests.get(f"https://web.cvm.gov.br/app/fundosweb/patrimonioLiquido/getPatrimoniosLiquidos/{id_registro}", timeout=1.5).json()
    except:
        try:
            info_pat = requests.get(f"https://web.cvm.gov.br/app/fundosweb/patrimonioLiquido/getPatrimoniosLiquidos/{id_registro}", timeout=3).json()
        except:
            info_pat = requests.get(f"https://web.cvm.gov.br/app/fundosweb/patrimonioLiquido/getPatrimoniosLiquidos/{id_registro}", timeout=6).json()
    return info_pat
    
def informar_atualizacao_patrimonial_fip(fundo, usuarios):
#422748
    
    v_atual = 0

    try:
        v_atual = get_ticker_value(fundo)
    except:
        pass

    info_b3 = buscar_info_b3_infra(fundo)
    info_pat = buscar_info_patrimonio_fip(info_b3["cnpj"])

    mensagem = "Informação patrimonial:"
    #mensagem += f'FII: {doc["codigoFII"]}'
    mensagem += f'\n\n\U0001F3E0Código: {fundo}'
    
    competencia = str(int(info_pat[0]["dataPatrimonioLiquido"][5:7])//3)+"T/"+info_pat[0]["dataPatrimonioLiquido"][:4]
    #if re.match(r"^\d{4}/\d{2}/\d{2}$",competencia):
        #competencia = format_dt_ambima(competencia)
        
    mensagem += f"\n\U0001F5D3Competência: {competencia}\n"
    
    #print(d)
    pl = info_pat[0]["valorPatrimonioLiquido"]
    if(len(info_pat) > 1):
        valz = round(pl / info_pat[1]["valorPatrimonioLiquido"]*100-100,4)
    qt_cotas = int(info_b3["quotaCount"])
    vp = pl/qt_cotas
    pvp = round(v_atual/vp,2)
    
    mensagem += f'\n\U0001F4CAPat. líquido: {convv(pl)}'
    
    if(len(info_pat) > 1):
        if valz > 0:
            valz = f"+{valz}%".replace(".",",")
            mensagem += f'\n\U0001F4C8Variação: {valz}'
        elif valz < 0:
            valz = f"{valz}%".replace(".",",")
            mensagem += f'\n\U0001F4C9Variação: {valz}'
        else:
            valz = f"0,00%"
            mensagem += f'\n\U0001F4C9Variação: {valz}'
        
    vp = f'R$ {round(vp*100//1/100,2):.2f}'.replace(".",",")
    
    pvp = f"{pvp:.2f}".replace(".",",")
    
    mensagem += f'\n\U0001F4B5VP/cota: {vp}'
    if v_atual:
        mensagem += f'\n\u2797P/VP atual: {pvp}'
    #mensagem += f'\n\u26A0Alavancagem: {alavancagem:.2%}'.replace(".",",")
        
    #print(mensagem)
    
    #print(convv(pl))
    #print(valz)
    #print(vp)
    #print(pvp)
        
    mensagem += "\n\n@RepositorioDeFIIs"
    for u in usuarios:
        bot.send_message(u, mensagem)

def informar_atualizacao_patrimonial_infra(fundo, usuarios):
#422748
    
    v_atual = 0

    try:
        v_atual = get_ticker_value(fundo)
    except:
        pass

    info_b3 = buscar_info_b3_infra(fundo)
    info_pat = buscar_info_patrimonio_infra(info_b3["cnpj"])

    mensagem = "Informação patrimonial:"
    #mensagem += f'FII: {doc["codigoFII"]}'
    mensagem += f'\n\n\U0001F3E0Código: {fundo}'
    
    competencia = info_pat[0]["dataPatrimonioLiquido"][8:10]+"/"+info_pat[0]["dataPatrimonioLiquido"][5:7]+"/"+info_pat[0]["dataPatrimonioLiquido"][:4]
    #if re.match(r"^\d{4}/\d{2}/\d{2}$",competencia):
        #competencia = format_dt_ambima(competencia)
        
    mensagem += f"\n\U0001F5D3Data ref.: {competencia}\n"
    
    #print(d)
    pl = info_pat[0]["valorPatrimonioLiquido"]
    if(len(info_pat) > 1):
        valz = round(pl / info_pat[1]["valorPatrimonioLiquido"]*100-100,4)
    qt_cotas = int(info_b3["quotaCount"])
    vp = pl/qt_cotas
    pvp = round(v_atual/vp,2)
    
    mensagem += f'\n\U0001F4CAPat. líquido: {convv(pl)}'
    
    """if(len(info_pat) > 1):
        if valz > 0:
            valz = f"+{valz}%".replace(".",",")
            mensagem += f'\n\U0001F4C8Variação: {valz}'
        elif valz < 0:
            valz = f"{valz}%".replace(".",",")
            mensagem += f'\n\U0001F4C9Variação: {valz}'
        else:
            valz = f"0,00%"
            mensagem += f'\n\U0001F4C9Variação: {valz}'"""
        
    vp = f'R$ {round(vp*100//1/100,2):.2f}'.replace(".",",")
    
    pvp = f"{pvp:.2f}".replace(".",",")
    
    mensagem += f'\n\U0001F4B5VP/cota: {vp}'
    if v_atual:
        mensagem += f'\n\u2797P/VP atual: {pvp}'
    #mensagem += f'\n\u26A0Alavancagem: {alavancagem:.2%}'.replace(".",",")
        
    #print(mensagem)
    
    #print(convv(pl))
    #print(valz)
    #print(vp)
    #print(pvp)
        
    mensagem += "\n\n@RepositorioDeFIIs"
    for u in usuarios:
        bot.send_message(u, mensagem)

async def env_msg_telethon():
    await client.send_message(int("5747986812"), "ativar")

def ativar_render():
    while True:
        try:
            time.sleep(900)
            requests.get("https://aaa-2jrx.onrender.com")
            """loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            with TelegramClient("x", TELETHON_API_ID, TELETHON_API_HASH).start() as client:
                loop.run_until_complete(asyncio.wait([env_msg_telethon()]))"""
        except:
            traceback.print_exc()

#Thread(target=thread_teste).start()
Thread(target=verificacao_periodica, daemon=False).start()
Thread(target=verificacao_periodica_infra, daemon=False).start()
Thread(target=thread_fechamento, daemon=True).start()
Thread(target=request_flask_thread).start()
#Thread(target=ativar_render, daemon=True).start()
#Thread(target=informar_fechamento2, daemon=True).start()
#bot.set_my_commands([telebot.types.BotCommand(comando[0], comando[1]) for comando in comandos])
#informar_provento_infra("BDIF11", "1.35", "16/10/2023", "23/10/2023")
#bot.infinity_polling(timeout=200, long_polling_timeout = 5)

"""provx = ultimo_provento_infra["CDII11"]
provy = buscar_ultimo_provento_infra("CDII11")
provy[0]['codigo'] = 'CDII12'
print("\n ------- \n")
print(provx)
print("\n ------- \n")
print(provy)
print("\n ------- \n")
print(comparar_proventos_infra(provx, provy))"""

#docs = buscar_documentos_infra(tokens_infra["JURO11"], agora()-datetime.timedelta(days=10))
#print(len(docs))
#env_infra("JURO11", docs[0], ["556068392","-743953207","556068392"])

#https://web.cvm.gov.br/app/fundosweb/consultarFundo/getRegistrosPorFiltro
#https://web.cvm.gov.br/app/fundosweb/registrarFundo/getRegistroFundoPorIdParaConsulta/5903
#https://web.cvm.gov.br/app/fundosweb/patrimonioLiquido/getPatrimoniosLiquidos/17189

#informar_atualizacao_patrimonial_fip("AATH11", ["556068392"])
#informar_provento_infra1(buscar_ultimo_provento_infra("BDIF11"), base_infra.buscar_seguidores("BDIF11"))
#bot.send_message("727500403", "Parabéns! Agora você receberá todos os documentos e comunicados referentes ao fundo CPSH11.")

"""ticker = "JRDM11"
doc_rend = buscar_ultimo_documento_provento(buscar_cnpj(ticker))
doc_rend["codigoFII"] = ticker
informar_proventos(doc_rend, ["556068392"])"""

"""
h = {
"Host": "web.cvm.gov.br",
"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
'Accept': 'application/json, text/plain, */*',
'Accept-Language': 'pt-BR,es-CO;q=0.8,pt;q=0.6,en-US;q=0.4,en;q=0.2',
'Accept-Encoding': 'gzip, deflate, br',
'Referer': 'https://web.cvm.gov.br/',
'Content-Type': 'application/json;charset=utf-8',
'Authorization': '',
#'Content-Length': '237',
'Origin': 'https://web.cvm.gov.br',
'DNT': '1',
'Connection': 'keep-alive',
'Cookie': 'JSESSIONID=q4LARhQMk30UtvtMibmRTju6eNjFKs7SNMdu696s.cd-appjp-03',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-origin'
}

data = {"filtro":
 {
  "numeroRegistro":"34964179000119",
   "tipoRegistro":{"id":56}
 }
}
print("...")
id_consulta = requests.post("https://web.cvm.gov.br/app/fundosweb/consultarFundo/getRegistrosPorFiltro", json=data, timeout=1).json()[0]["id"]
print(id_consulta)

id_registro = requests.get(f"http://web.cvm.gov.br/app/fundosweb/registrarFundo/getRegistroFundoPorIdParaConsulta/{id_consulta}", timeout=1).json()["registro"]["id"]
print(id_registro)

info_pat = requests.get(f"https://web.cvm.gov.br/app/fundosweb/patrimonioLiquido/getPatrimoniosLiquidos/{id_registro}", timeout=1).json()[0]

print(f'{info_pat["valorPatrimonioLiquido"]/buscar_info_b3_infra(fundo)["quotaCount"]:.2f}')
"""
#print(r.json())
"""doc = buscar_ultimo_documento_provento(42888292000190)
doc["codigoFII"] = "JGPX11"
informar_proventos(doc,["556068392"])
doc = buscar_documentos(buscar_cnpj("APTO11"), agora()-datetime.timedelta(days=25))[0]
doc["codigoFII"] = "APTO11"
print(doc)
informar_atualizacao_patrimonial(doc, ["556068392"])"""
