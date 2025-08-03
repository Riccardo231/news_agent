#!/usr/bin/env python

import requests

def ollama_agent(prompt, model, ollama_url, max_tokens=2048):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": max_tokens}
    }
    try:
        response = requests.post(ollama_url, json=payload, timeout=180)
        data = response.json()
        return data.get("response", "[Nessuna risposta da Ollama]")
    except Exception as e:
        return f"[Errore chiamando Ollama: {e}]"

def agent_riassunto(article, model, ollama_url):
    prompt = (
        f"Leggi la seguente notizia e fornisci un riassunto breve, chiaro e oggettivo.\n\n"
        f"TITOLO: {article['title']}\n\n"
        f"TESTO: {article['summary']}\n"
        f"(Autore/Fonte: {article['author']}, Data: {article['date']})"
    )
    return ollama_agent(prompt, model, ollama_url)

def agent_implicazioni(article, riassunto, model, ollama_url):
    prompt = (
        f"Hai letto questa notizia (riassunta):\n\n"
        f"RIASSUNTO: {riassunto}\n\n"
        f"Titolo: {article['title']}\n"
        f"Analizza le possibili implicazioni, conseguenze sociali, economiche, tecniche e politiche che derivano da questa notizia."
        f"Sii concreto e ragionato, anche ipotizzando scenari realistici per il futuro."
    )
    return ollama_agent(prompt, model, ollama_url)

def agent_teoria(article, riassunto, implicazioni, model, ollama_url):
    prompt = (
        f"Considerando questa notizia:\n"
        f"TITOLO: {article['title']}\n"
        f"RIASSUNTO: {riassunto}\n"
        f"IMPLICAZIONI: {implicazioni}\n\n"
        f"Costruisci una possibile teoria, spiegazione complessiva o scenario più ampio "
        f"che possa mettere insieme il significato della notizia e delle sue conseguenze, anche collegando ad altri fenomeni globali o a sviluppi futuri."
    )
    return ollama_agent(prompt, model, ollama_url)

def summarize_with_ollama(articles, model, ollama_url):
    N = 30
    if not articles:
        return "[Nessun articolo disponibile]"
    testo = "\n".join([f"{a['title']} — {a['summary']}" for a in articles[:N]])
    prompt = (
        "Hai una lista di notizie del giorno:\n\n"
        f"{testo}\n\n"
        "Fai un sunto ragionato delle principali notizie (max 10 righe), estrapola i temi ricorrenti, "
        "le notizie di maggiore impatto e commenta brevemente. Scrivi in italiano, risposta discorsiva."
    )
    return ollama_agent(prompt, model, ollama_url)
