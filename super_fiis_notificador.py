from firebase_admin import messaging

import firebase_admin

from firebase_admin import credentials

cred = credentials.Certificate("super-fiis-firebase-adminsdk-b7b42-5b9aacf64a.json")

firebase_admin.initialize_app(cred)

def notificar_seguidores_documento_fundo_bot(fundo, d):

    dados = {}
    msg = ""
    titulo = ""

    de = d["dataEntrega"]
    #print(datetime.datetime(year=int(de[6:10]), month=int(de[3:5]), day=int(de[0:2]), hour=int(de[11:13])), desde)
    if d["status"] == "AC":
        identificador = d["id"]
        nome_arquivo = d['categoriaDocumento'].strip() + " - "
        if "Relatório Gerencial" in d['tipoDocumento'] or "Informes Periódicos" in d['categoriaDocumento']:
            nome_arquivo = ""
        if len(d['tipoDocumento'].strip()) > 0:
            nome_arquivo += d['tipoDocumento'].strip() + " - "
        if len(d['especieDocumento'].strip()) > 0:
            nome_arquivo += d['especieDocumento'].strip() + " - "
        nome_arquivo = nome_arquivo[:-3]
        if "Informes Periódicos" in d['categoriaDocumento']:
            nome_arquivo += f" ({d['dataReferencia']})"
        if "Relatório Gerencial" in d['tipoDocumento']:
            nome_arquivo += f" ({d['dataReferencia'].strip()[3:10]})"
        if "Fato Relevante" in d['categoriaDocumento'] or "Regulamento" == d['categoriaDocumento'].strip():
            nome_arquivo += f" ({d['dataEntrega'].strip()[:10]})"
        extensao = "pdf" if "Relatório" in nome_arquivo else None
        data = d["dataEntrega"]
        
        dados["identificador"] = str(identificador)
        dados["titulo"] = nome_arquivo
        if extensao:
            dados["extensao"] = extensao
        dados["tipo"] = "documento"
        #dados["documento"]["identificador"] = 
        #dados["documento"]["identificador"] = 
        
        
        return enviar_notificacao(fundo, f"{fundo} - {nome_arquivo}", msg, dados)
        
        #lista.append(Documento(identificador, buscar_fundo_pelo_cnpj(cnpj), nome_arquivo, extensao, data))
#lista.reverse()


def enviar_notificacao(fundo, titulo, mensagem = "", dados = {}):
    message = messaging.Message(data=dados,
        android=messaging.AndroidConfig(
            collapse_key=None,
            priority='high',
            notification=messaging.AndroidNotification(
                title=titulo,
                body=mensagem,
                #icon='ic_launcher',
            ),
        ),
        topic=fundo,
        #token=registration_token
    )
    # [END android_message]
    return messaging.send(message)