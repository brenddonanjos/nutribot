from flask import Flask, Response, request, session, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import secrets
import json
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
CORS(app, supports_credentials=True, origins="*")

URL_ROBO = "http://localhost:5000"
CONFIANCA_MINIMA = os.getenv("CONFIANCA_MINIMA", 0.6)
ROTA_ALIVE = f"{URL_ROBO}/alive"
ROTA_CONVERSAR = f"{URL_ROBO}/conversar"
ROTA_PESQUISAR_RECEITA = f"{URL_ROBO}/receitas"
TIPO_DEFAULT = "com_ingredientes"

def acessa_servico(url, payload):
  error = None
  resposta = None
  try:    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
      resposta = response.json()
  except Exception as e:
    error = str(e)
    print(f"Erro ao acessar serviço: {str(e)}")

  return error, resposta


def pergunta_robo(pergunta):
  erro = None
  modo_pesquisa = False
  mensagem = "Infelizmente, ainda não sei responder esta pergunta. Tente pesquisar na internet ou consultar um profissional de nutrição especialista."

  erro, resposta = acessa_servico(ROTA_CONVERSAR, {"pergunta": pergunta})
  if resposta and resposta["confianca"] >= float(CONFIANCA_MINIMA):
      mensagem = resposta["resposta"]
      modo_pesquisa = verifica_modo_pesquisa(mensagem)
    
  return erro, mensagem, modo_pesquisa

def verifica_modo_pesquisa(resposta_robo):
  resposta_robo = resposta_robo.strip()
  gatilho = "Vamos iniciar sua pesquisa por receitas! Informe os ingredientes separados por vírgula para que eu possa encontrar as receitas adequadas."
  return resposta_robo == gatilho

def pesquisa_receita(ingredientes, tipo):
  erro = None
  receitas = []
  ingredientes = ingredientes.split(',')

  erro, resposta = acessa_servico(ROTA_PESQUISAR_RECEITA, {"ingredientes": ingredientes, "tipo": tipo})

  if erro is None and resposta:
    receitas = resposta["receitas"]
  
  return erro, receitas

@app.get("/")
def index():
  return render_template("index.html")

@app.post("/chat")
def chat():
  content = request.json
  resposta = ""
  receitas = []

  pesquisa_ativa = "modo_pesquisa" in session.keys() and session["modo_pesquisa"]
  tipo = session["tipo"] if "tipo" in session.keys() else TIPO_DEFAULT
  
  if pesquisa_ativa:
    session["modo_pesquisa"] = False
    
    ingredientes = content["pergunta"].lower()
    erro, receitas = pesquisa_receita(ingredientes, tipo)
    if len(receitas):
      resposta = "Caso deseje refazer a pesquisa, digite 'pesquisar novamente' ou pressione o botão de pesquisa 🔍"
    else: 
      resposta = "Infelizmente, não encontrei receitas com os ingredientes informados. Tente novamente com outros ingredientes."
  else: 
    erro, resposta, modo_pesquisa = pergunta_robo(content["pergunta"].lower())
    if erro != None:
      return Response({"error": erro}, status=500)

    if modo_pesquisa:
      session["modo_pesquisa"] = True
      if "tipo" in content.keys():
        session["tipo"] = content["tipo"]
      else:
        session["tipo"] = TIPO_DEFAULT
      
      resposta = f"RECEITAS SEM INGREDIENTES:\nVamos iniciar sua pesquisa por receitas! Informe os ingredientes que você deseja evitar separados por vírgula." if session["tipo"] == "sem_ingredientes" else f"RECEITAS COM INGREDIENTES:\n{resposta}"

  session["receitas_selecionadas"] = json.dumps(receitas)

  return Response(json.dumps({"resposta": resposta, "receitas": receitas}), status=200, mimetype="application/json")

@app.get("/receitas/<path:nome_arquivo>")
def download_receita(nome_arquivo):
  return send_from_directory("static/receitas", nome_arquivo, as_attachment=True)

if __name__ == "__main__":
  app.run(
    host = "0.0.0.0",
    port = 5001,
    debug=True
  )
