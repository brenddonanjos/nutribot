#!/bin/bash

echo "Instalando dependências..."
pip install -r requirements.txt

echo "Baixando modelo spaCy (en_core_web_sm)..."
python3 -m spacy download en_core_web_sm
python3 -m spacy download pt_core_news_sm

echo "Executando o script de treinamento..."
python3 treino.py

echo "Executando o processamento de receitas..."
python3 processa_receitas.py

python3 servico.py

