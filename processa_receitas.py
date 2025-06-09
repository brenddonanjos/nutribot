from nltk import word_tokenize, corpus
from nltk.corpus import floresta
from string import punctuation
import sqlite3
import os
import json
from dotenv import load_dotenv
load_dotenv()

PATH_RECEITAS = "chat/static/receitas/"
PATH_PALAVRAS_INDESEJADAS = "regras/palavras_indesejadas.json"
PATH_REGRAS_CLASSIFICACAO = "regras/regras_classificacao.json"
BD_RECEITAS = os.getenv("BD_RECEITAS", "bd/receitas.sqlite3")
CLASSES_GRAMATICAIS_INDESEJADAS = [
  "adv",
  "v-inf",
  "v-fin",
  "v-pcp",
  "v-ger",
  "num",
  "adj"
]


def inicializar():
  palavras_de_parada = set(corpus.stopwords.words("portuguese"))
  classificacoes = {}
  for (palavra, classificacao) in floresta.tagged_words():
      classificacoes[palavra.lower()] = classificacao

  return palavras_de_parada, classificacoes


def ler_conteudo_arquivo(path_arquivo):
  sucesso = False
  conteudo = None

  if os.path.isfile(path_arquivo) and nome_arquivo.endswith(".txt"):
    try: 
      with open(path_arquivo, "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()
        arquivo.close()
        sucesso = True
    except Exception as e:
      print(f"Erro ao ler o arquivo {path_arquivo}: {e}")
  else:
    print(f"Arquivo {path_arquivo} não encontrado ou não é um arquivo de texto.")
  
  return sucesso, conteudo

def extrair_titulo(conteudo):
  titulo = None
  marcador = "Título: "

  if conteudo: 
    linhas = conteudo.splitlines() #Separa o conteúdo em linhas
    for linha in linhas:
      if linha.startswith(marcador):
        titulo = linha[len(marcador):].strip()
        break

  return titulo

def extrair_ingredientes_texto(conteudo):
  marcador_inicio = "Ingredientes:"
  marcador_fim = "Modo de Preparo:"
  texto_ingredientes = ""

  if conteudo: 
    marcador_inicio = conteudo.find(marcador_inicio) + len(marcador_inicio)
    marcador_fim = conteudo.find(marcador_fim)
    if marcador_inicio != -1 and marcador_fim != -1:
      texto_ingredientes = conteudo[marcador_inicio:marcador_fim].strip()

  return texto_ingredientes

def extrair_modo_preparo(conteudo):
  marcador_inicio = "Modo de Preparo:"
  marcador_fim = "Informações Adicionais:"
  texto_modo_preparo = ""

  if conteudo: 
    marcador_inicio = conteudo.find(marcador_inicio) + len(marcador_inicio)
    marcador_fim = conteudo.find(marcador_fim)
    if marcador_fim == -1: marcador_fim = len(conteudo)
    if marcador_inicio != -1:
      texto_modo_preparo = conteudo[marcador_inicio:marcador_fim].strip()

  return texto_modo_preparo

def extrair_tipos_refeicao(conteudo):
  marcador_inicio = "Tipo:"
  marcador_fim = "Objetivo/Restrição:"
  tipo_refeicao = ""

  if conteudo: 
    marcador_inicio = conteudo.find(marcador_inicio) + len(marcador_inicio)
    marcador_fim = conteudo.find(marcador_fim)
    if marcador_inicio != -1 and marcador_fim != -1:
      tipo_refeicao = conteudo[marcador_inicio:marcador_fim].strip()
  
  return tipo_refeicao

def extrair_objetivos_restricoes(ingredientes):
  objetivos_restricoes = []
  regras = None

  try:
    with open(PATH_REGRAS_CLASSIFICACAO, "r", encoding="utf-8") as arquivo:
      regras = json.load(arquivo)
  except Exception as e: 
      print(f"Erro ao ler o arquivo de regras: {e}")

  if regras:
    teste = []
    for objetivo, regra in regras.items():
      proibidos = regra.get("proibidos", [])
      if proibidos and len(proibidos) > 0: 
        teste.append(proibidos)

    return teste
  
  return objetivos_restricoes

def remove_palavras_de_parada(tokens, palavras_de_parada):
  tokens_filtrados = []

  for token in tokens:
    if token not in palavras_de_parada:
      tokens_filtrados.append(token)

  return tokens_filtrados

def remove_pontuacao(tokens):
  tokens_filtrados = []

  for token in tokens:
    if token not in punctuation:
      tokens_filtrados.append(token)

  return tokens_filtrados

def remove_classes_indesejadas(tokens, classificacoes):
  tokens_filtrados = []

  for token in tokens:
      if token in classificacoes.keys():
        classificacao = classificacoes[token]
        if not any (s in classificacao for s in CLASSES_GRAMATICAIS_INDESEJADAS):
          tokens_filtrados.append(token)
      else:
        isDigit = token[:1].isdigit()
        if not isDigit:
          tokens_filtrados.append(token)

  return tokens_filtrados

def remove_palavras_indesejadas(tokens):
  tokens_filtrados = []
  tokens = list(set(tokens)) #Usa o set para remover duplicatas
  palavras_indesejadas = []

  try: 
    with open(PATH_PALAVRAS_INDESEJADAS, "r", encoding="utf-8") as arquivo:
      conteudo = json.load(arquivo)
      if conteudo and "palavras" in conteudo:
        palavras_indesejadas = conteudo["palavras"]

      arquivo.close()
  except Exception as e:
    print(f"Erro ao ler o arquivo {path_arquivo}: {e}")

  if palavras_indesejadas and len(palavras_indesejadas) > 0:
    for token in tokens:
      if token not in palavras_indesejadas:
        tokens_filtrados.append(token)
  else:
    tokens_filtrados = tokens

  return tokens_filtrados

def inicia_banco():
  if os.path.exists(BD_RECEITAS):
    os.remove(BD_RECEITAS)

  con = sqlite3.connect(BD_RECEITAS)

  cursor = con.cursor()
  cursor.execute("CREATE TABLE IF NOT EXISTS receitas (id INTEGER PRIMARY KEY AUTOINCREMENT, arquivo TEXT, titulo TEXT, ingredientes TEXT, tipos_refeicao TEXT, objetivos_restricoes TEXT, modo_preparo TEXT )")

def salva_receita(arquivo, titulo, ingredientes, tipos_refeicao, objeivos_restricoes, modo_preparo):
  con = sqlite3.connect(BD_RECEITAS)
  cursor = con.cursor()
  insert = "INSERT INTO receitas (arquivo, titulo, ingredientes, tipos_refeicao, objetivos_restricoes, modo_preparo) VALUES (?, ?, ?, ?, ?, ?)"
  cursor.execute(
    insert, 
    (arquivo, titulo, ingredientes, tipos_refeicao, objeivos_restricoes, modo_preparo)
  )
  con.commit()
  con.close()

def lista_receitas():
  con = sqlite3.connect(BD_RECEITAS)
  con.row_factory = sqlite3.Row
  cursor = con.cursor()
  cursor.execute("SELECT * FROM receitas")
  receitas = cursor.fetchall()
  con.close()

  return receitas

if __name__ == "__main__":
  palavras_de_parada, classificacoes = inicializar()
  conteudo_dos_arquivos = {}
  inicia_banco()

  if os.path.isdir(PATH_RECEITAS):
    try:
      for nome_arquivo in os.listdir(PATH_RECEITAS):
        path_arquivo = os.path.join(PATH_RECEITAS, nome_arquivo)
        sucesso, conteudo = ler_conteudo_arquivo(path_arquivo)
        if sucesso:
          #titulo
          titulo = extrair_titulo(conteudo)

          #ingredientes
          ingredientes_texto = extrair_ingredientes_texto(conteudo)
          ingredientes = word_tokenize(ingredientes_texto.lower(), language="portuguese")
          ingredientes = remove_palavras_de_parada(ingredientes, palavras_de_parada)
          ingredientes = remove_pontuacao(ingredientes)
          ingredientes = remove_classes_indesejadas(ingredientes, classificacoes)
          ingredientes = remove_palavras_indesejadas(ingredientes)

          #preparo
          preparo = extrair_modo_preparo(conteudo)

          #tipos de refeição (Almoço, jantar...)
          tipos_refeicao = extrair_tipos_refeicao(conteudo)

          #objetivos/restricoes
          objetivos_restricoes = ""
          # objetivos_restricoes = extrair_objetivos_restricoes(ingredientes)

          salva_receita(nome_arquivo, titulo, str(ingredientes), tipos_refeicao, objetivos_restricoes, preparo)
          print(f"Receita {titulo } salva!")

    except Exception as e:
      print(f"Erro ao ler o diretório de receitas: {e}")
  else:
    print(f"Diretório de receitas não encontrado: {PATH_RECEITAS}")
  
  


  
