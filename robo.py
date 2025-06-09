from chatterbot import ChatBot
from dotenv import load_dotenv
import os
import ast
from processa_receitas import lista_receitas

load_dotenv()

NOME_ROBO =  os.getenv("NOME_ROBO", "Robô Nutricionista Goes")
BD_ROBO = os.getenv("BD_ROBO", "bd/chat.sqlite3")
BD_RECEITAS =  os.getenv("BD_RECEITAS", "bd/receitas.sqlite3")
CONFIANCA_MINIMA = os.getenv("CONFIANCA_MINIMA", 0.6)

def inicializar():
    sucesso = False
    robo = None

    try:
        robo = ChatBot(
          NOME_ROBO, 
          read_only=True, 
          storage_adapter="chatterbot.storage.SQLStorageAdapter", 
          database_uri=f"sqlite:///{BD_ROBO}"
        )
        sucesso = True
    except Exception as e:
        print(f"erro inicializando o robô: {str(e)}")

    return sucesso, robo

def receitas_com_ingredientes(ingredientes):
    receitas = lista_receitas()
    receitas_selecionadas = []
    sucesso = False
    if receitas:
        for receita in receitas:
            ingredientes_receita = ast.literal_eval(receita['ingredientes'].lower()) #transforma em lista
            if any(ingrediente.lower() in ingredientes_receita for ingrediente in ingredientes):
                receitas_selecionadas.append({
                    "arquivo": receita["arquivo"],
                    "titulo": receita["titulo"]
                })
                sucesso = True
    
    return sucesso, receitas_selecionadas

def receitas_sem_ingredientes(ingredientes):
    receitas = lista_receitas()
    receitas_selecionadas = []
    sucesso = False
    if receitas:
        for receita in receitas:
            ingredientes_receita = ast.literal_eval(receita['ingredientes'].lower()) 
            if not any(ingrediente.lower() in ingredientes_receita for ingrediente in ingredientes):
                receitas_selecionadas.append({
                    "arquivo": receita["arquivo"],
                    "titulo": receita["titulo"]
                })
                sucesso = True
    return sucesso, receitas_selecionadas



def executar(robo):
    while True:
        mensagem = input("👤 ")
        resposta = robo.get_response(mensagem.lower())

        if resposta.confidence >= float(CONFIANCA_MINIMA):
            print(f"🤖 {resposta.text} [confiança {CONFIANCA_MINIMA} - {resposta.confidence:.2f}]")
        else:
            print(f"🤖 Infelizmente, ainda não sei responder esta pergunta. Tente pesquisar na internet ou consultar um profissional de nutrição especialista.")

if __name__ == "__main__":
    sucesso, robo = inicializar()
    if sucesso:
        executar(robo)