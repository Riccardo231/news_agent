#!/usr/bin/env python3

from news_agent.settings import load_settings
from news_agent.verifier import NewsVerifier

print("=== TEST SERPAPI ===")

# Carica impostazioni
settings = load_settings()
print(f"Settings caricate: {list(settings.keys())}")

# Controlla serpapi_key
serpapi_key = settings.get("serpapi_key")
print(f"serpapi_key presente: {bool(serpapi_key)}")
if serpapi_key:
    print(f"serpapi_key lunghezza: {len(serpapi_key)}")
    print(f"serpapi_key primi 10 caratteri: {serpapi_key[:10]}...")
    print(f"serpapi_key.strip() vuoto: {not serpapi_key.strip()}")

# Prova a creare il verifier
if serpapi_key and serpapi_key.strip():
    try:
        verifier = NewsVerifier(serpapi_key)
        print("✅ Verifier creato con successo!")
        print(f"Verifier presente: {bool(verifier)}")
    except Exception as e:
        print(f"❌ Errore creazione verifier: {e}")
else:
    print("❌ serpapi_key non valida")

print("=== FINE TEST ===") 