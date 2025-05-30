from flask import Flask, Response, request
from flask_cors import CORS
from robo import *

import json

sucesso, robo = inicializar()
service = Flask(NOME_ROBO)
CORS(service)

@service.get("/alive")
def is_alive():
  return Response(json.dumps({"alive": "sim" if sucesso else "não"}), status=200, mimetype="application/json")

@service.post("/conversar")
def get_resposta():
  if sucesso:
    conteudo = request.json
    resposta = robo.get_response(conteudo["pergunta"].lower())

    return Response(
      json.dumps({
        "resposta": resposta.text, 
        "confianca": resposta.confidence
      }), 
      status=200, 
      mimetype="application/json"
    )
  else:
    return Response(status=503)
  
@service.post("/receitas")
def get_receitas():  
  conteudo = request.json
  ingredientes = conteudo['ingredientes'].split(',')
  ingredientes = [ingrediente.strip() for ingrediente in ingredientes]

  sucesso, receitas = receitas_com_ingredientes(ingredientes)

  return Response(
    json.dumps({"receitas": receitas}), 
    status=200 if sucesso else 204, 
    mimetype="application/json"
  )

if __name__ == "__main__":
  service.run(host="0.0.0.0", port=5000, debug=True)