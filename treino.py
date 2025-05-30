from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from dotenv import load_dotenv
import os
import json

load_dotenv()

CONVERSAS = [
  "conversas/informacoes.json",
  "conversas/saudacoes.json",
  "conversas/pesquisa.json"
]

NOME_ROBO = os.getenv("NOME_ROBO", "Robô Nutricionista Goes")
BD_ROBO = os.getenv("BD_ROBO", "bd/chat.sqlite3")

def cria_treinador():
  robo = ChatBot(
    NOME_ROBO, 
    storage_adapter = "chatterbot.storage.SQLStorageAdapter", 
    database_uri=f"sqlite:///{BD_ROBO}"
  )
  robo.storage.drop()

  return ListTrainer(robo)

def obter_conversas():
    conversas = []
    for arquivo_conversas in CONVERSAS:
      with open(arquivo_conversas, "r", encoding="utf-8") as arquivo:
        lista_conversas = json.load(arquivo)
        conversas.append(lista_conversas["conversas"])
        arquivo.close()

    return conversas

def treinar(treinador, conversas):
    for conversa in conversas:
      for mensagens_resposta in conversa:
        mensagens = mensagens_resposta["mensagens"]
        resposta = mensagens_resposta["resposta"]

        for mensagem in mensagens:
          print(f"treinando pergunta: {mensagem}, resposta: {resposta}")
          treinador.train([mensagem, resposta])

if __name__ == "__main__":
    treinador = cria_treinador()
    conversas = obter_conversas()
    if treinador and conversas:
      treinar(treinador, conversas)
      print("Treinamento concluído com sucesso!")