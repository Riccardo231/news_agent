#!/usr/bin/env python3

from news_agent.settings import load_settings
from news_agent.verifier import NewsVerifier
from news_agent.ui import show_table

print("=== TEST MAIN ===")

# Carica impostazioni
settings = load_settings()
serpapi_key = settings.get("serpapi_key")
print(f"serpapi_key: {bool(serpapi_key)}")

# Crea verifier
verifier = None
if serpapi_key and serpapi_key.strip():
    try:
        verifier = NewsVerifier(serpapi_key)
        print(f"✅ Verifier creato: {bool(verifier)}")
    except Exception as e:
        print(f"❌ Errore verifier: {e}")
        verifier = None
else:
    print("❌ serpapi_key non valida")

# Test show_table
print(f"\nTest show_table con has_serpapi={bool(verifier)}")
articles = [{'title': 'Test', 'date': '2025-01-01', 'author': 'Test', 'link': '#'}]
try:
    show_table(articles, 1, 1, 0, has_serpapi=bool(verifier))
    print("✅ show_table eseguita")
except Exception as e:
    print(f"❌ Errore show_table: {e}")

print("=== FINE TEST ===") 