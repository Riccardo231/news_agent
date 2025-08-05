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

def agent_analisi_universale(article, model, ollama_url):
    """Agente con framework di analisi multi-tematica universale e metodologico"""
    
    framework_prompt = f"""
# FRAMEWORK DI ANALISI MULTI-TEMATICA UNIVERSALE
## Metodologia: Analisi Critica Strutturata

### CONTESTO DELL'ARTICOLO
**Titolo:** {article['title']}
**Fonte:** {article['author']}
**Data:** {article['date']}
**Contenuto:** {article['summary']}

---

## 1. ANALISI FATTUALE (FACTUAL ANALYSIS)
### 1.1 Identificazione dei Fatti Principali
- Estrai i fatti verificabili e oggettivi
- Distingui tra fatti e opinioni
- Identifica le fonti citate e la loro affidabilità

### 1.2 Contesto Storico e Geografico
- Colloca l'evento nel contesto storico appropriato
- Identifica il contesto geografico e culturale
- Evidenzia eventuali precedenti rilevanti

---

## 2. ANALISI MULTI-DIMENSIONALE (MULTI-DIMENSIONAL ANALYSIS)
### 2.1 Dimensioni Sociali
- Impatto sulle comunità e sui gruppi sociali
- Dinamiche di potere e relazioni sociali
- Cambiamenti nelle norme sociali o culturali

### 2.2 Dimensioni Economiche
- Impatto economico diretto e indiretto
- Effetti su mercati, settori o economie
- Implicazioni per la distribuzione della ricchezza

### 2.3 Dimensioni Politiche
- Impatto su istituzioni e processi politici
- Effetti su policy e governance
- Dinamiche di potere e influenza

### 2.4 Dimensioni Tecnologiche
- Implicazioni tecnologiche e innovative
- Effetti su infrastrutture e sistemi
- Cambiamenti nelle capacità tecniche

### 2.5 Dimensioni Ambientali
- Impatto ambientale e sostenibilità
- Effetti su risorse naturali
- Implicazioni per il cambiamento climatico

---

## 3. ANALISI CRITICA (CRITICAL ANALYSIS)
### 3.1 Bias e Limiti
- Identifica potenziali bias nella narrazione
- Evidenzia limiti metodologici o informativi
- Considera prospettive alternative

### 3.2 Credibilità e Affidabilità
- Valuta la credibilità delle fonti
- Analizza la qualità delle informazioni
- Identifica eventuali contraddizioni

### 3.3 Interessi e Agende
- Identifica potenziali interessi in gioco
- Analizza le agende delle parti coinvolte
- Considera il contesto di potere

---

## 4. ANALISI PROSPETTIVA (FORWARD-LOOKING ANALYSIS)
### 4.1 Scenari Probabili
- Sviluppi più probabili nel breve termine
- Trend di medio-lungo periodo
- Punti di svolta potenziali

### 4.2 Implicazioni Strategiche
- Opportunità e minacce emergenti
- Implicazioni per decisioni strategiche
- Necessità di adattamento o cambiamento

### 4.3 Domande Aperte
- Aree di incertezza e ambiguità
- Domande che richiedono ulteriori indagini
- Aspetti che necessitano monitoraggio

---

## 5. SINTESI METODOLOGICA (METHODOLOGICAL SYNTHESIS)
### 5.1 Livello di Confidenza
- Valuta la solidità delle conclusioni
- Identifica le basi di evidenza
- Considera l'incertezza residua

### 5.2 Raccomandazioni
- Suggerimenti per ulteriori analisi
- Aree che richiedono attenzione
- Priorità per il monitoraggio

---

## OUTPUT RICHIESTO
Fornisci un'analisi strutturata seguendo questo framework. Sii:
- **Obiettivo**: Basa l'analisi sui fatti disponibili
- **Sistematico**: Segui la struttura metodologica
- **Critico**: Considera prospettive multiple
- **Prospettico**: Guarda oltre il presente immediato
- **Pratico**: Fornisci insights utilizzabili

Rispondi in italiano, usando una struttura chiara con sezioni e sottosezioni.
"""
    
    return ollama_agent(framework_prompt, model, ollama_url, max_tokens=4096)

def agent_verifica(article, verification_data, model, ollama_url):
    """Agente per valutare la veridicità di una notizia basandosi sui dati di verifica"""
    fact_check_results = verification_data.get('fact_check_results', [])
    reliable_results = verification_data.get('reliable_sources_results', [])
    
    # Prepara i dati per l'analisi
    fact_check_text = ""
    if fact_check_results and not fact_check_results[0].get('error'):
        fact_check_text = "\n".join([
            f"- {result.get('title', '')}: {result.get('snippet', '')}"
            for result in fact_check_results[:3]
        ])
    
    reliable_text = ""
    if reliable_results and not reliable_results[0].get('error'):
        reliable_text = "\n".join([
            f"- {result.get('title', '')} ({result.get('source', '')})"
            for result in reliable_results[:3]
        ])
    
    prompt = (
        f"Analizza la veridicità della seguente notizia basandoti sui dati di verifica forniti.\n\n"
        f"NOTIZIA DA VERIFICARE:\n"
        f"Titolo: {article['title']}\n"
        f"Riassunto: {article['summary']}\n"
        f"Fonte: {article['author']}\n"
        f"Data: {article['date']}\n\n"
        f"DATI DI FACT-CHECKING:\n{fact_check_text}\n\n"
        f"FONTI AFFIDABILI:\n{reliable_text}\n\n"
        f"VALUTAZIONE:\n"
        f"1. Analizza la credibilità della fonte originale\n"
        f"2. Confronta con i risultati di fact-checking\n"
        f"3. Verifica la presenza di fonti affidabili che confermano\n"
        f"4. Identifica eventuali contraddizioni o red flag\n"
        f"5. Fornisci un giudizio finale: VERITIERA, DUBBIA, o FALSA\n"
        f"6. Spiega il ragionamento dietro la tua valutazione\n\n"
        f"Rispondi in italiano in modo chiaro e strutturato."
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
