# src/config.py
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Recuperar a chave da API do Google Maps
GOOGLE_MAPS_API_KEY = os.getenv('GMAPIKEY')

if GOOGLE_MAPS_API_KEY is None:
    raise ValueError("A chave da API do Google Maps (GMAPIKEY) não foi encontrada no arquivo .env")
