#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import re

def ollama_agent(prompt, ai_provider, max_tokens=2048):
    """Funzione wrapper per compatibilità con il vecchio sistema"""
    return ai_provider.generate(prompt, max_tokens)

def scrape_article_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        if 'news.google.com/rss/articles' in url:
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()
            if 'consent.google.com' in response.url:
                headers['Accept'] = 'application/rss+xml, application/xml, text/xml'
                headers['Accept-Language'] = 'en-US,en;q=0.9'
                response = requests.get(url, headers=headers, timeout=10, allow_redirects=False)
            soup = BeautifulSoup(response.content, 'xml')
            link_element = soup.find('link')
            if link_element:
                real_link = link_element.text.strip()
                if real_link and real_link.startswith('http'):
                    url = real_link
                else: return None
            else: return None
        elif 'news.google.com' in url:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            selectors = [
                'a[href*="http"]:not([href*="google.com"])', 'a[data-n-tid]', 'a[jslog]',
                'article a[href*="http"]', '.VDXfz a[href*="http"]', 'a[href*="repubblica"]',
                'a[href*="corriere"]', 'a[href*="ansa"]', 'a[href*="ilfatto"]',
                'a[href*="lastampa"]', 'a[href*="ilsole24ore"]', 'a[href*="ilpost"]',
                'a[href*="ilmanifesto"]'
            ]
            real_link = None
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    href = link.get('href')
                    if href and 'google.com' not in href and href.startswith('http'):
                        real_link = href
                        break
                if real_link: break
            if not real_link: return None
            url = real_link

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']): tag.decompose()
        content_selectors = ['article', '[class*="content"]', '[class*="article"]', '[class*="post"]', '.entry-content', '.post-content', '.article-content', 'main']
        content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                content = ' '.join([elem.get_text(strip=True) for elem in elements])
                if len(content) > 200: break
        if not content or len(content) < 200:
            body = soup.find('body')
            if body: content = body.get_text(strip=True)
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\'\"]', '', content)
        if len(content) > 5000: content = content[:5000] + "..."
        return content
    except Exception as e: return None

def get_article_full_content(article):
    content = scrape_article_content(article['link'])
    if not content: return article['summary']
    return content

def agent_riassunto(article, ai_provider):
    content = get_article_full_content(article)
    prompt = (
        f"Leggi la seguente notizia e fornisci un riassunto breve, chiaro e oggettivo.\n\n"
        f"TITOLO: {article['title']}\n\n"
        f"TESTO COMPLETO: {content}\n"
        f"(Autore/Fonte: {article['author']}, Data: {article['date']})"
    )
    return ai_provider.generate(prompt, max_tokens=500)

def agent_implicazioni(article, riassunto, ai_provider):
    content = get_article_full_content(article)
    prompt = (
        f"Hai letto questa notizia (riassunta):\n\n"
        f"RIASSUNTO: {riassunto}\n\n"
        f"TESTO COMPLETO: {content}\n\n"
        f"Titolo: {article['title']}\n"
        f"Analizza le possibili implicazioni, conseguenze sociali, economiche, tecniche e politiche che derivano da questa notizia."
        f"Sii concreto e ragionato, anche ipotizzando scenari realistici per il futuro."
    )
    return ai_provider.generate(prompt, max_tokens=600)

def agent_teoria(article, riassunto, implicazioni, ai_provider):
    content = get_article_full_content(article)
    prompt = (
        f"Considerando questa notizia:\n"
        f"TITOLO: {article['title']}\n"
        f"RIASSUNTO: {riassunto}\n"
        f"IMPLICAZIONI: {implicazioni}\n\n"
        f"TESTO COMPLETO: {content}\n\n"
        f"Costruisci una possibile teoria, spiegazione complessiva o scenario più ampio "
        f"che possa mettere insieme il significato della notizia e delle sue conseguenze, anche collegando ad altri fenomeni globali o a sviluppi futuri."
    )
    return ai_provider.generate(prompt, max_tokens=700)

def summarize_with_ollama(articles, ai_provider):
    N = 15
    if not articles: return "[Nessun articolo disponibile]"
    testo = "\n".join([f"{a['title']}" for a in articles[:N]])
    prompt = (
        "Hai una lista di titoli di notizie del giorno:\n\n"
        f"{testo}\n\n"
        "Fai un sunto ragionato delle principali notizie (max 8 righe), estrapola i temi ricorrenti, "
        "le notizie di maggiore impatto e commenta brevemente. Scrivi in italiano, risposta discorsiva."
    )
    return ai_provider.generate(prompt, max_tokens=1024)

def summarize_article(article, ai_provider):
    content = get_article_full_content(article)
    prompt = (
        f"Leggi questo articolo e fornisci un riassunto dettagliato e ben strutturato.\n\n"
        f"TITOLO: {article['title']}\n"
        f"FONTE: {article['author']}\n"
        f"DATA: {article['date']}\n\n"
        f"CONTENUTO COMPLETO:\n{content}\n\n"
        f"Fornisci un riassunto di 8-10 righe che includa:\n"
        f"- I fatti principali\n"
        f"- Il contesto\n"
        f"- Le implicazioni principali\n"
        f"Scrivi in italiano in modo chiaro e oggettivo."
    )
    return ai_provider.generate(prompt, max_tokens=500)

def agent_verifica(article, verification_data, ai_provider):
    fact_check_results = verification_data.get('fact_check_results', [])
    reliable_results = verification_data.get('reliable_sources_results', [])
    
    fact_check_content = ""
    if fact_check_results and not fact_check_results[0].get('error'):
        for result in fact_check_results[:3]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            
            if full_content:
                fact_check_content += f"\n--- ARTICOLO: {title} ({source}) ---\n{full_content}\n"
            else:
                fact_check_content += f"\n--- ARTICOLO: {title} ({source}) ---\n{snippet}\n"
    
    reliable_content = ""
    if reliable_results and not reliable_results[0].get('error'):
        for result in reliable_results[:3]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            
            if full_content:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\n{full_content}\n"
            else:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\n{snippet}\n"
    
    title = article.get('title', 'Testo personalizzato')
    summary = article.get('summary', '')
    author = article.get('author', 'Fonte sconosciuta')
    date = article.get('date', 'Data non disponibile')
    
    prompt = (
        f"Analizza la veridicità della seguente notizia basandoti sui dati di verifica forniti.\n\n"
        f"NOTIZIA DA VERIFICARE:\n"
        f"Titolo: {title}\n"
        f"Riassunto: {summary}\n"
        f"Fonte: {author}\n"
        f"Data: {date}\n\n"
        f"ARTICOLI DI FACT-CHECKING:\n{fact_check_content}\n\n"
        f"FONTI AFFIDABILI:\n{reliable_content}\n\n"
        f"VALUTAZIONE:\n"
        f"1. Analizza la credibilità della fonte originale\n"
        f"2. Confronta con i risultati di fact-checking\n"
        f"3. Verifica la presenza di fonti affidabili che confermano\n"
        f"4. Identifica eventuali contraddizioni o red flag\n"
        f"5. Fornisci un giudizio finale: VERITIERA, DUBBIA, o FALSA\n"
        f"6. Spiega il ragionamento dietro la tua valutazione\n\n"
        f"Rispondi in italiano in modo chiaro e strutturato."
    )
    
    return ai_provider.generate(prompt, max_tokens=800)

def agent_validazione_verita(article, verification_data, ai_provider):
    fact_check_results = verification_data.get('fact_check_results', [])
    reliable_results = verification_data.get('reliable_sources_results', [])
    
    fact_check_content = ""
    if fact_check_results and not fact_check_results[0].get('error'):
        for result in fact_check_results[:3]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            
            if full_content:
                fact_check_content += f"\n--- FACT-CHECK: {title} ({source}) ---\n{full_content}\n"
            else:
                fact_check_content += f"\n--- FACT-CHECK: {title} ({source}) ---\n{snippet}\n"
    
    reliable_content = ""
    if reliable_results and not reliable_results[0].get('error'):
        for result in reliable_results[:3]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            
            if full_content:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\n{full_content}\n"
            else:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\n{snippet}\n"
    
    title = article.get('title', 'Testo personalizzato')
    summary = article.get('summary', '')
    author = article.get('author', 'Fonte sconosciuta')
    date = article.get('date', 'Data non disponibile')
    
    prompt = (
        f"Sei un esperto di fact-checking. Valuta la veridicità di questa notizia.\n\n"
        f"🔍 NOTIZIA DA VALIDARE:\n"
        f"📰 Titolo: {title}\n"
        f"📝 Riassunto: {summary}\n"
        f"🏢 Fonte: {author}\n"
        f"📅 Data: {date}\n\n"
        f"🔎 RISULTATI FACT-CHECKING:\n{fact_check_content}\n\n"
        f"✅ FONTI AFFIDABILI:\n{reliable_content}\n\n"
        f"🎯 VALUTAZIONE FINALE:\n"
        f"Devi fornire:\n"
        f"1. **VERDETTO**: [VERA] / [FALSA] / [DUBBIA] / [INSUFFICIENTI DATI]\n"
        f"2. **CONFIDENZA**: [ALTA] / [MEDIA] / [BASSA] (quanto sei sicuro del verdetto)\n"
        f"3. **MOTIVAZIONE**: Spiega brevemente perché hai dato questo verdetto\n"
        f"4. **RED FLAG**: Eventuali segnali di allarme (bias, fonti sospette, contraddizioni)\n"
        f"5. **CONFERME**: Fonti che supportano o contraddicono la notizia\n\n"
        f"Rispondi in modo diretto e chiaro, evidenziando il verdetto finale."
    )
    
    return ai_provider.generate(prompt, max_tokens=600)
