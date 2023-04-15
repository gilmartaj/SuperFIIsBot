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

import time

from bs4 import BeautifulSoup

import pytz

import traceback

client = gspread.service_account(filename='superfiisbot-9f67df851d9a.json')

sheet = client.open("SeguidoresFIIs").sheet1
sheet_infra = client.open("SeguidoresFI-Infras").sheet1

telebot.apihelper.SESSION_TIME_TO_LIVE = 60 * 15

bot_aux = os.getenv("bot_aux_token")
bot_super = os.getenv("bot_super_token")

TELETHON_API_ID = os.getenv("telethon_api_id")
TELETHON_API_HASH = os.getenv("telethon_api_hash")

bot = telebot.TeleBot(bot_super)



comandos = [
    ("start", "Iniciar"),
    ("ajuda", "Exibe a mensagem de ajuda."),
    ("cnpj", 'Exibe o CNPJ de um FII. Ex.: "/cnpj URPR11".'),
    ("contato", "Exibe informações para contato."),
    ("cotacao", 'Mostra a cotação de um fundo imobiliário. Ex.: "/cotacao URPR11"'),
    ("docs", 'Receba os documentos emitidos pelo fundo nos últimos 30 dias. Ex.: "/docs URPR11"'),
    ("desinscrever", 'Use para deixar de seguir um FII que você segue. Ex.: "/desinscrever URPR11"'),
    ("doacao", "Ajude a manter o projeto vivo doando a partir de 1 centavo. Chave Pix: gil77891@gmail.com"),
    ("fundos_seguidos", "Lista todos os fundos imobiliários que você segue."),
    ("rend", 'Informa a última distribuição de proventos do fundo. Ex.: "/rend URPR11"'),
    ("seguir", 'Use para receber todos os documentos e informações de rendimentos de um FII. Ex.: "/seguir URPR11"'), 
    ("ultimos_documentos", 'Receba os documentos emitidos pelo fundo nos últimos 30 dias. Ex.: "/ultimos_documentos URPR11"'),
    #("teste", "Teste"),
    ]

fiis_cnpj = pd.read_csv("fiis_cnpj.csv", dtype={"Código":str, "CNPJ":str}).dropna()
 



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
        return sorted(seguidos)
        
    def buscar_seguidores(self, fii):
            return list(filter(lambda s: s != "", self.planilha[fii]))
            
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
                mensagem += f'\n\U0001F5D3Data base: {conv_data(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["DataBase"])}'
                mensagem += f'\n\U0001F4B8Data de pagamento: {conv_data(dados["DadosEconomicoFinanceiros"]["InformeRendimentos"]["Provento"]["Rendimento"]["DataPagamento"])}'
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
    for u in usuarios:
        bot.send_message(u, mensagem)

def informar_fechamento2():
    dic = {}
    usuarios = base.buscar_todos_usuarios()
    usuarios.remove("-1001894911077")
    usuarios.append("-1001894911077")
    #usuarios.insert(0, "556068392")
    print(usuarios)

    for usuario in usuarios:#usuarios:#base.buscar_todos_seguidores:
        fs = base.buscar_seguidos(usuario)
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
                    msg2 = f"\U0001F6AAFECHAMENTO ({h.day:02d}/{h.month:02d}/{h.year})\n" + msg[msg.index("\n", 3850):msg.index("\n", 6600)] + "\n\n@RepositorioDeFIIs\n@SuperFIIsBot"
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
                    v, variacao = get_ticker_variacao2(f)
                    time.sleep(5)
                    if not v or v=="0,00":
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
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=1&s=0&l=10&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}")
    lista = []
    for d in r.json()["data"]:
        de = d["dataEntrega"]
        #print(datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13])), desde)
        if datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13]), minute=int(de[14:16]), tzinfo=tz_info) < desde:
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
        if datetime.datetime(year=int(de[0:4]), month=int(de[5:7]), day=int(de[8:10]), hour=int(de[11:13]), minute=int(de[14:16]), tzinfo=tz_info) < desde:
            break
        lista.append(d)
        print(d)
    lista.reverse()
    return lista
    
async def enviar_documento_1(usuario, nome_doc, caption,client):
    
        with open(nome_doc, "rb") as fp:
            z = await client.send_file(usuario, file=fp, caption=caption)
            return z.file.id
            
def compartilhar_documento_enviado(usuarios, file_id, caption):
    for u in usuarios:
            bot.send_document(
            u,
            file_id,
            caption=caption
            )

def baixar_documento_1(link, nome_doc, cabecalhos={}):
    with open(nome_doc, "wb") as f:
        f.write(requests.get(link, headers=cabecalhos).content)
            
def env_infra(cod_fundo, doc, usuarios):
    if len(usuarios) < 1:
        return
      
    nome_doc = doc["name"].replace("/","_") + ".pdf"
    link = f'https://bvmf.bmfbovespa.com.br/sig/FormConsultaPdfDocumentoFundos.asp?strSigla={cod_fundo[:-2]}&strData={doc["date"]}'
    baixar_documento_1(link, nome_doc, cabecalhos={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"})
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    file_id = 0
    caption = cod_fundo + " - " + doc["name"] + "\n\n@RepositorioDeFIIs\n@SuperFiisBot"
    with TelegramClient("bot", TELETHON_API_ID, TELETHON_API_HASH).start(bot_token=bot_super) as client:
        x = loop.run_until_complete(asyncio.wait([enviar_documento_1(int(usuarios[0]), nome_doc, caption,client)]))
        file_id = list(x[0])[0].result()
    os.remove(nome_doc)
    print(file_id)
    if len(usuarios) > 1:
        compartilhar_documento_enviado(usuarios[1:], file_id, caption)

    
def buscar_ultimo_documento_provento(cnpj):
    rend = None
    r = requests.get(f"https://fnet.bmfbovespa.com.br/fnet/publico/pesquisarGerenciadorDocumentosDados?d=1&s=0&l=100&o%5B0%5D%5BdataEntrega%5D=desc&cnpjFundo={cnpj}")
    for d in r.json()["data"]:
        tipo = d["tipoDocumento"]
        #print(datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13])), desde)
        if tipo.strip() == "Rendimentos e Amortizações":
            return d
    return None
        
def baixarDocumento(link):
    pass

def envio_multiplo(doc, file_id, usuarios, caption_):
    for u in usuarios:
            bot.send_document(
            u,
            file_id,
            visible_file_name="Informe.pdf",
            caption=caption_
            )
  
def envio_multiplo_telebot(doc, usuarios, caption_):
    if len(usuarios) <= 0:
        return
        
    dx = bot.send_document(
            usuarios[0],
            xml_pdf(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}'),
            visible_file_name="Informe.pdf",
            caption=caption_
            )
    if len(usuarios) > 1:        
        envio_multiplo(doc, dx.document.file_id, usuarios[1:], caption_)
        
def envio_multiplo_telethon(doc, usuarios):
    if len(usuarios) <= 0:
        return
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tipo_doc = doc["tipoDocumento"].replace("/", "-") if doc["tipoDocumento"].strip() != "" else doc["categoriaDocumento"]
    with TelegramClient("bot", TELETHON_API_ID, TELETHON_API_HASH).start(bot_token=bot_super) as client:
     with open(f'{tipo_doc}.pdf', "wb") as f:
        f.write(requests.get(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}', headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"}).content)
        loop.run_until_complete(asyncio.wait([ enviar_documento( doc, int(usuarios[0]), client)]))
        #print("LLLLLLLLLLLLLLLL")
     os.remove(f'{tipo_doc}.pdf')
    
    if len(usuarios) > 1:
        tipo_doc = doc["tipoDocumento"].replace("/", "-") if doc["tipoDocumento"].strip() != "" else doc["categoriaDocumento"]
        if tipo_doc == "Relatório Gerencial":
            data_ref = re.search(r"\d\d/\d\d\d\d", doc["dataReferencia"])
        else:
            data_ref = re.search(r"\d\d/\d\d/\d\d\d\d", doc["dataReferencia"])
        data_ref = "("+data_ref.group()+")" if data_ref else doc["dataReferencia"].replace("/", "-").replace(":", "-")     
        envio_multiplo(doc, doc["file_id"], usuarios[1:], f'{doc["codigoFII"]} - {doc["tipoDocumento"]} {data_ref}\n\n@RepositorioDeFIIs')

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
             with open(f'{tipo_doc}.pdf', "wb") as f:
                f.write(requests.get(f'https://fnet.bmfbovespa.com.br/fnet/publico/exibirDocumento?id={doc["id"]}', headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"}).content)
                loop.run_until_complete(asyncio.wait([ enviar_documento( doc, usuario, client)]))
             os.remove(f'{tipo_doc}.pdf')
           
   
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
            with open(f'{tipo_doc}.pdf', "rb") as fp:
                    z = await client.send_file(usuario, file=fp, caption=f'{doc["codigoFII"]} - {tipo_doc} {data_ref}\n\n@RepositorioDeFIIs')
                    #print("ID:", z.file.id)
                    #telebot.TeleBot(bot_super).send_document(usuario, z.file.id, caption="TESTE")
                    doc["file_id"] = z.file.id
    
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
    try:
        ticker = message.text.split()[1].strip().upper()
        val, var = get_ticker_variacao2(ticker)
        bot.send_message(message.chat.id, str(val)+"\n"+str(var), reply_to_message_id=message.id)
    except:
        traceback.print_exc()
    """doc_rend = buscar_ultimo_documento_provento(buscar_cnpj(ticker))
    if doc_rend:
        doc_rend["codigoFII"] = ticker
        informar_proventos(doc_rend, message.from_user.id)
    else:
        bot.send_message(message.chat.id, f'Não encontramos informações sobre a última distribuição deste fundo.', reply_to_message_id=message.id)"""



@bot.message_handler(commands=["rend"])
def handle_command(message):
    #cmd = message.text.split()[0]
    #print(message)
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        if not ticker in base.colunas():
            if ticker in ("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                bot.send_message(message.chat.id, f"Desculpe, mas no momento esta função não está disponível para FI-Infras.", reply_to_message_id=message.id)
                return
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo imobiliário {ticker}.", reply_to_message_id=message.id)
            return
        doc_rend = buscar_ultimo_documento_provento(buscar_cnpj(ticker))
        if doc_rend:
            doc_rend["codigoFII"] = ticker
            informar_proventos(doc_rend, [message.from_user.id])
        else:
            bot.send_message(message.chat.id, f'Não encontramos informações sobre a última distribuição de proventos deste fundo.', reply_to_message_id=message.id)    
    elif len(message.text.strip().split()) == 1:
        bot.send_message(message.chat.id, f'Informe o código de negociação do fundo imobiliário que você deseja ver informações sobre a última distribuições de proventos.\nEx.: "/rend URPR11".', reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Uso incorreto. Para ver informações sobre a última distribuição de proventos de um fundo, envie /rend CODIGO_FUNDO.\nEx.: "/rend URPR11".', reply_to_message_id=message.id)





            
@bot.message_handler(commands=["docs", "ultimos_documentos"])
def handle_command(message):
    cmd = message.text.split()[0]
    #print(message)
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        if not ticker in base.colunas():
            if ticker in ("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                #bot.send_message(message.chat.id, f"Desculpe, mas no momento não temos a opção ver de documentos de FI-Infras.", reply_to_message_id=message.id)
                bot.send_message(message.chat.id, f"Buscando documentos...")
                documentos = buscar_documentos_infra(tokens_infra[ticker], agora()-datetime.timedelta(days=30))
                #print(documentos)
                if len(documentos) == 0:
                    bot.send_message(message.chat.id, f"O FII-Infra imobiliário {ticker} não disponibilizaou nenhum documento nos últimos 30 dias.")
                    return
                for doc in documentos:
                    print(ticker, "-", doc["name"])
                    #doc["codigoFII"] = ticker
                    env_infra(ticker, doc, [message.from_user.id])
                return
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo listado {ticker}.", reply_to_message_id=message.id)
            return
        bot.send_message(message.chat.id, f"Buscando documentos...")
        documentos = buscar_documentos2(buscar_cnpj(ticker), datetime.datetime.now() - datetime.timedelta(days=30))
        #print(documentos)
        if len(documentos) == 0:
            bot.send_message(message.chat.id, f"O fundo imobiliário {ticker} não disponibilizaou nenhum documento nos últimos 30 dias.")
            return
        for doc in documentos:
            print(ticker, "-", doc["tipoDocumento"])
            doc["codigoFII"] = ticker
            env(doc, message.from_user.id)
            #if doc["tipoDocumento"] == "Rendimentos e Amortizações":
                #informar_proventos(doc, message.from_user.id)
    elif len(message.text.strip().split()) == 1:
        bot.send_message(message.chat.id, f'Informe o código de negociação do fundo imobiliário que você deseja ver os últimos documentos.\nEx.: "{cmd} URPR11".', reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, f'Uso incorreto. Para receber os comunicados mais recentes de um fundo, envie {cmd} CODIGO_FUNDO.\nEx.: "{cmd} URPR11".', reply_to_message_id=message.id)

@bot.message_handler(commands=["seguir"])
def handle_command(message):
    #print(message)
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        ticker = message.text.split()[1].strip().upper()
        r = base.inserir(ticker, str(message.chat.id))
        if r == 0:
            bot.send_message(message.chat.id, f"Parabéns! Agora você receberá todos os documentos e comunicados referentes ao fundo {ticker}.", reply_to_message_id=message.id)
        elif r == 1:
            bot.send_message(message.chat.id, "Você já segue esse fundo. Assim que forem divulgados novos documentos ou comunicados, lhe enviaremos.", reply_to_message_id=message.id)
        elif r == -1:
            if ticker in ("BODB11", "BDIF11", "CPTI11", "BIDB11", "IFRA11", "KDIF11", "OGIN11", "RBIF11", "CDII11", "JURO11", "SNID11", "XPID11"):
                bot.send_message(message.chat.id, f"Desculpe, mas no momento não temos a opção de seguir FI-Infras.", reply_to_message_id=message.id)
            else:
                bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo imobiliário {ticker}.", reply_to_message_id=message.id)
    else:
        bot.send_message(message.chat.id, 'Uso incorreto. Para seguir um fundo envie /seguir CODIGO_FUNDO. Ex.: "/seguir URPR11"', reply_to_message_id=message.id)
        
@bot.message_handler(commands=["desinscrever"])
def handle_command(message):
    #print(message)
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
        bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo imobiliário {ticker}.", reply_to_message_id=message.id)
        
@bot.message_handler(commands=["fundos_seguidos"])
def handle_command(message):
    #print(message)
    print(message.from_user.first_name, message.text)
    fs = base.buscar_seguidos(str(message.from_user.id))
    if len(fs) == 0:
        bot.send_message(message.chat.id, f"Você ainda não está seguindo nenhum fundo imobiliário. Para começar, utilize o comando /seguir", reply_to_message_id=message.id)
    else:
        resposta = "FIIs que você segue:"
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
       
        
@bot.message_handler(regexp=r"(\s)*/cotacao.* [A-Za-z]{4}11")
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
    print(agora(), message.from_user.first_name, message.text)
    if len(message.text.strip().split()) == 2:
        try:
            ticker = message.text.split()[1].strip()
            cnpj = buscar_cnpj(ticker.upper())
            bot.send_message(message.chat.id, cnpj, reply_to_message_id=message.id)
        except:
            bot.send_message(message.chat.id, f"Não encontramos em nossa base de dados o fundo imobiliário {ticker}.")
    else:
        bot.send_message(message.chat.id, 'Uso incorreto. Para ver o CNPJ um fundo envie /cnpj CODIGO_FUNDO. Ex.: "/cnpj URPR11"', reply_to_message_id=message.id)

def mensagem_instrucoes():
    msg = ""
    for comando, descricao in comandos:
        msg += f"/{comando}: {descricao}\n"
    return msg

@bot.message_handler(commands=["start"])
def handle_command(message):
    #print(message)
    #bot.forward_message("-743953207", message.chat.id, message.id)
    bot.send_message("-743953207", f"{message.from_user.first_name} ({message.from_user.id}) {message.text}")
    print(agora(), message.from_user.first_name, message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Seja bem-vindo ao @SuperFIIsBot!!!\n\n")
    bot.send_message(message.from_user.id, "Segue a lista de comandos disponíveis e suas respectivas descrições:\n\n"+mensagem_instrucoes())
    bot.send_message(message.from_user.id, "Em caso de dúvidas ou sugestões, entre em contato diretamente com o desenvolvedor @gilmartaj, ficaremos felizes em ajudar!")
    
@bot.message_handler(commands=["ajuda"])
def handle_command(message):
    #print(message)
    print(agora(), message.from_user.first_name, message.text)
    bot.send_message(message.from_user.id, "Segue a lista de comandos disponíveis e suas respectivas descrições:\n\n"+mensagem_instrucoes()+"\nEm caso de dúvidas ou sugestões, entre em contato diretamente com o desenvolvedor @gilmartaj", reply_to_message_id=message.id)
    
@bot.message_handler(commands=["doacao"])
def handle_command(message):
    print(agora(), message.from_user.first_name, message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Além do tempo de desenvolvimento, manter o bot rodando exige um servidor, e isso tem um custo. Se o bot é útil para você e não lhe fazem falta alguns centavos, ajude o projeto doando a partir de 1 centavo para a Chave Pix de e-mail do desenvolvedor: gil77891@gmail.com\n\nObs.: Não use este e-mail para contato, isto pode ser feito aqui mesmo pelo Telegram, enviando uma mensagem para @gilmartaj.")
    
@bot.message_handler(commands=["contato"])
def handle_command(message):
    print(agora(), message.from_user.first_name, message.from_user.id, message.text)
    bot.send_message(message.from_user.id, "Para dúvidas, sugestões e reportes de erros, envie uma mensagem direta para o desenvolvedor @gilmartaj, aqui mesmo pelo Telegram.")


def verificar():
    #print("Verificando...")
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
                    try:
                        for seg in seguidores:
                            seg = int(seg)
                            env(doc, seg)
                    except:
                        ultima_busca[f] = h
                    if doc["tipoDocumento"] == "Rendimentos e Amortizações":
                        #for seg in seguidores:
                            #seg = int(seg)
                       informar_proventos(doc, seguidores)
                    elif "Informe Mensal Estruturado" in doc["tipoDocumento"]:
                        informar_atualizacao_patrimonial(doc, seguidores)
                except:
                    traceback.print_exc()
                    
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
            Thread(target=verificar, daemon=True).start()
            h = agora()
            if is_dia_util(h.date()) and h.hour > 7 and h.hour < 22:
                time.sleep(600)
            else:
                time.sleep(3600)
                print("Verificando...")
        except:
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
    parada = datetime.datetime(h.year, h.month, h.day, 18, 0, tzinfo=h.tzinfo)
    if h.hour >= 18:
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
    docs = buscar_documentos(buscar_cnpj("FAED11"), desde=agora()-datetime.timedelta(days=30))  
    print(len(docs))
    for doc in docs:
        doc["codigoFII"] = "FAED11"
        env2(doc, ["-495713843", "556068392"])
        
tz_info = agora().tzinfo
      
ultima_busca = {}
for f in base.colunas():
    ultima_busca[f] = agora()
    
ultima_busca_infra = {}
for f in base_infra.colunas():
    ultima_busca_infra[f] = agora() - datetime.timedelta(days=1)
    
def verificar_infra():
    #print("Verificando...")
    for f in base_infra.colunas():
        seguidores = base_infra.buscar_seguidores(f)
        if len(seguidores) > 0:
            #print(f, len(seguidores))
            h = ultima_busca_infra[f]
            ultima_busca_infra[f] = agora()
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
                except:
                    ultima_busca_infra[f] = h

def verificacao_periodica_infra():
    time.sleep(900)

    while True:
        try:
            Thread(target=verificar_infra, daemon=True).start()
            h = agora()
            if is_dia_util(h.date()) and h.hour > 7 and h.hour < 22:
                time.sleep(3600)
            else:
                time.sleep(10000)
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
    "OGIN11": "eyJpZGVudGlmaWVyRnVuZCI6Ik9HSU4iLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "RBIF11": "eyJpZGVudGlmaWVyRnVuZCI6IlJCSUYiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "SNID11": "eyJpZGVudGlmaWVyRnVuZCI6IlNOSUQiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
    "XPID11": "eyJpZGVudGlmaWVyRnVuZCI6IlhQSUQiLCJ0eXBlIjoxLCJwYWdlTnVtYmVyIjoxLCJwYWdlU2l6ZSI6MjB9",
}
    
       
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
        print("Comp")
        
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
        
    vp = f'R$ {round(vp*100//1/100,2)}'.replace(".",",")
    
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

#Thread(target=thread_teste).start()
#Thread(target=thread_fechamento, daemon=True).start()
Thread(target=verificacao_periodica, daemon=True).start()
Thread(target=verificacao_periodica_infra, daemon=True).start()
bot.set_my_commands([telebot.types.BotCommand(comando[0], comando[1]) for comando in comandos])

bot.infinity_polling(timeout=200, long_polling_timeout = 5)

#docs = buscar_documentos_infra(tokens_infra["JURO11"], agora()-datetime.timedelta(days=10))
#print(len(docs))
#env_infra("JURO11", docs[0], ["556068392","-743953207","556068392"])

"""doc = buscar_ultimo_documento_provento(42888292000190)
doc["codigoFII"] = "JGPX11"
informar_proventos(doc,["556068392"])
doc = buscar_documentos(buscar_cnpj("APTO11"), agora()-datetime.timedelta(days=25))[0]
doc["codigoFII"] = "APTO11"
print(doc)
informar_atualizacao_patrimonial(doc, ["556068392"])"""