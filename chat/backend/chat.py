from flask import Flask, Response, request, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import secrets
import json

load_dotenv()

app = Flask("NutriBot")
app.secret_key = secrets.token_hex(16)
CORS(app)

URL_ROBO = "http://localhost:5000"
CONFIANCA_MINIMA = os.getenv("CONFIANCA_MINIMA", 0.6)
ROTA_ALIVE = f"{URL_ROBO}/alive"
ROTA_CONVERSAR = f"{URL_ROBO}/conversar"

def perguntar_robo(pergunta):
  sucesso = False
  resposta = None
  modo_pesquisa = False
  try:
    import requests
    response = requests.post(ROTA_CONVERSAR, json={"pergunta": pergunta})
    if response.status_code == 200:
      sucesso = True
      resposta = response.json()
      modo_pesquisa = verifica_modo_pesquisa(resposta)
  except Exception as e:
    print(f"Erro ao comunicar com o robô: {str(e)}")
  return sucesso, resposta, modo_pesquisa

def verifica_modo_pesquisa(resposta_robo):
  return "Vamos iniciar sua pesquisa por receitas! Informe os ingredientes separados por vírgula" in resposta_robo

@app.post("/chat")
def chat():
  content = request.json
  sucesso, resposta, modo_pesquisa = perguntar_robo(content["pergunta"].lower())

  if not sucesso:
    return Response(status=503)
  
  if modo_pesquisa:
    session["modo_pesquisa"] = True
  
  if resposta["confianca"] < float(CONFIANCA_MINIMA):
    resposta = {
      "resposta": "Infelizmente, ainda não sei responder esta pergunta. Tente pesquisar na internet ou consultar um profissional de nutrição especialista."
    }

  return Response(json.dumps({"response": resposta}), status=200, mimetype="application/json")

if __name__ == "__main__":
  app.run(
    host = "0.0.0.0",
    port = 5001,
    debug=True
  )
