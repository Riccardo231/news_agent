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
        for result in fact_check_results[:5]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            search_query = result.get('search_query', '')
            language = result.get('language', 'it')
            
            # Traduci automaticamente i contenuti in inglese
            if language == 'en':
                title = f"[TRADOTTO] {title}"
                if full_content:
                    full_content = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {full_content}"
                else:
                    snippet = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {snippet}"
            
            if full_content:
                fact_check_content += f"\n--- FACT-CHECK: {title} ({source}) ---\nQuery: {search_query}\n{full_content}\n"
            else:
                fact_check_content += f"\n--- FACT-CHECK: {title} ({source}) ---\nQuery: {search_query}\n{snippet}\n"
    
    reliable_content = ""
    if reliable_results and not reliable_results[0].get('error'):
        for result in reliable_results[:5]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            search_query = result.get('search_query', '')
            language = result.get('language', 'it')
            
            if language == 'en':
                title = f"[TRADOTTO] {title}"
                if full_content:
                    full_content = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {full_content}"
                else:
                    snippet = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {snippet}"
            
            if full_content:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\nQuery: {search_query}\n{full_content}\n"
            else:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\nQuery: {search_query}\n{snippet}\n"
    
    title = article.get('title', 'Testo personalizzato')
    summary = article.get('summary', '')
    author = article.get('author', 'Fonte sconosciuta')
    date = article.get('date', 'Data non disponibile')
    
    prompt = (
        f"Sei un analista di intelligence esperto. Analizza la veridicità della seguente notizia.\n\n"
        f"🔍 NOTIZIA DA VERIFICARE:\n"
        f"📰 Titolo: {title}\n"
        f"📝 Riassunto: {summary}\n"
        f"🏢 Fonte: {author}\n"
        f"📅 Data: {date}\n\n"
        f"🔎 FONTI DISPONIBILI:\n{fact_check_content}\n\n"
        f"✅ FONTI AFFIDABILI:\n{reliable_content}\n\n"
        f"🎯 ANALISI CRITICA E INTELLIGENTE:\n"
        f"1. **VERDETTO**: [VERA] / [FALSA] / [DUBBIA] / [INSUFFICIENTI DATI]\n"
        f"2. **LIVELLO DI CONFIDENZA**: [ALTO 90%+] / [MEDIO 70-90%] / [BASSO <70%]\n"
        f"3. **FATTI OGGETTIVI**: Elenca solo i fatti realmente verificabili e misurabili\n"
        f"4. **VALUTAZIONE DEGLI STUDI SCIENTIFICI**: Analizza:\n"
        f"   - Metodologia dello studio (campione, controlli, peer review)\n"
        f"   - Finanziamenti e conflitti di interesse\n"
        f"   - Critiche o repliche esistenti\n"
        f"   - Consenso scientifico sul tema\n"
        f"   - Qualità della rivista e del processo di revisione\n"
        f"5. **CONTROVERSE E DIBATTITI**: Elenca versioni diverse, interpretazioni alternative\n"
        f"6. **BIAS IDENTIFICATI**: Bias delle fonti, pressioni esterne, interessi economici\n"
        f"7. **MOTIVAZIONE**: Spiega il ragionamento critico\n\n"
        f"⚠️ METODO CRITICO E AUTONOMO:\n"
        f"- VALUTA ogni studio scientifico individualmente (metodologia, campione, peer review)\n"
        f"- Cerca CONTRADDIZIONI e INCOERENZE tra fonti\n"
        f"- Identifica CHI ha finanziato lo studio e eventuali conflitti di interesse\n"
        f"- Verifica se esistono CRITICHE o REPLICHE dello studio specifico\n"
        f"- Controlla il CONSENSO SCIENTIFICO sul tema (altri studi concordano?)\n"
        f"- Distingui tra FATTI OGGETTIVI e INTERPRETAZIONI/SPECULAZIONI\n"
        f"- Valuta la QUALITÀ della metodologia, non solo la fonte\n\n"
        f"🌐 Se trovi contenuti in inglese, traduci automaticamente le informazioni chiave.\n\n"
        f"Rispondi in modo diretto e critico, evidenziando il verdetto finale."
    )
    
    return ai_provider.generate(prompt, max_tokens=1000)

def agent_validazione_verita(article, verification_data, ai_provider):
    fact_check_results = verification_data.get('fact_check_results', [])
    reliable_results = verification_data.get('reliable_sources_results', [])
    
    fact_check_content = ""
    if fact_check_results and not fact_check_results[0].get('error'):
        for result in fact_check_results[:5]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            search_query = result.get('search_query', '')
            language = result.get('language', 'it')
            
            if language == 'en':
                title = f"[TRADOTTO] {title}"
                if full_content:
                    full_content = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {full_content}"
                else:
                    snippet = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {snippet}"
            
            if full_content:
                fact_check_content += f"\n--- FACT-CHECK: {title} ({source}) ---\nQuery: {search_query}\n{full_content}\n"
            else:
                fact_check_content += f"\n--- FACT-CHECK: {title} ({source}) ---\nQuery: {search_query}\n{snippet}\n"
    
    reliable_content = ""
    if reliable_results and not reliable_results[0].get('error'):
        for result in reliable_results[:5]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            search_query = result.get('search_query', '')
            language = result.get('language', 'it')
            
            if language == 'en':
                title = f"[TRADOTTO] {title}"
                if full_content:
                    full_content = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {full_content}"
                else:
                    snippet = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {snippet}"
            
            if full_content:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\nQuery: {search_query}\n{full_content}\n"
            else:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\nQuery: {search_query}\n{snippet}\n"
    
    title = article.get('title', 'Testo personalizzato')
    summary = article.get('summary', '')
    author = article.get('author', 'Fonte sconosciuta')
    date = article.get('date', 'Data non disponibile')
    
    prompt = (
        f"Sei un analista di intelligence esperto. Valuta la veridicità di questa notizia.\n\n"
        f"🔍 NOTIZIA DA VALIDARE:\n"
        f"📰 Titolo: {title}\n"
        f"📝 Riassunto: {summary}\n"
        f"🏢 Fonte: {author}\n"
        f"📅 Data: {date}\n\n"
        f"🔎 FONTI DISPONIBILI:\n{fact_check_content}\n\n"
        f"✅ FONTI AFFIDABILI:\n{reliable_content}\n\n"
        f"🎯 VALUTAZIONE CRITICA:\n"
        f"1. **VERDETTO**: [VERA] / [FALSA] / [DUBBIA] / [INSUFFICIENTI DATI]\n"
        f"2. **LIVELLO DI CONFIDENZA**: [ALTO 90%+] / [MEDIO 70-90%] / [BASSO <70%]\n"
        f"3. **FATTI OGGETTIVI**: Elenca solo i fatti realmente verificabili\n"
        f"4. **RED FLAG**: Identifica studi sospetti, ricostruzioni dubbie, bias delle fonti\n"
        f"5. **CONTROVERSE**: Elenca versioni diverse e interpretazioni alternative\n"
        f"6. **BIAS**: Identifica conflitti di interesse e pressioni esterne\n"
        f"7. **MOTIVAZIONE**: Spiega il ragionamento critico\n\n"
        f"⚠️ METODO CRITICO:\n"
        f"- NON fidarti di 'studi scientifici' o 'prove tecnologiche' automaticamente\n"
        f"- Cerca CONTRADDIZIONI e INCOERENZE\n"
        f"- Identifica CHI ha interesse a diffondere questa notizia\n"
        f"- Valuta la CREDIBILITÀ delle fonti, non la loro autorevolezza apparente\n"
        f"- Cerca EVIDENZE CONCRETE, non 'ricostruzioni' o 'simulazioni'\n\n"
        f"🌐 Se trovi contenuti in inglese, traduci automaticamente le informazioni chiave.\n\n"
        f"Rispondi in modo diretto e critico, evidenziando il verdetto finale."
    )
    
    return ai_provider.generate(prompt, max_tokens=800)

def agent_verifica_advanced(article, verification_data, ai_provider):
    """Agente di verifica con ragionamento complesso step-by-step"""
    fact_check_results = verification_data.get('fact_check_results', [])
    reliable_results = verification_data.get('reliable_sources_results', [])
    
    fact_check_content = ""
    if fact_check_results and not fact_check_results[0].get('error'):
        for result in fact_check_results[:5]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            search_query = result.get('search_query', '')
            language = result.get('language', 'it')
            
            if language == 'en':
                title = f"[TRADOTTO] {title}"
                if full_content:
                    full_content = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {full_content}"
                else:
                    snippet = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {snippet}"
            
            if full_content:
                fact_check_content += f"\n--- FACT-CHECK: {title} ({source}) ---\nQuery: {search_query}\n{full_content}\n"
            else:
                fact_check_content += f"\n--- FACT-CHECK: {title} ({source}) ---\nQuery: {search_query}\n{snippet}\n"
    
    reliable_content = ""
    if reliable_results and not reliable_results[0].get('error'):
        for result in reliable_results[:5]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            search_query = result.get('search_query', '')
            language = result.get('language', 'it')
            
            if language == 'en':
                title = f"[TRADOTTO] {title}"
                if full_content:
                    full_content = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {full_content}"
                else:
                    snippet = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {snippet}"
            
            if full_content:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\nQuery: {search_query}\n{full_content}\n"
            else:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\nQuery: {search_query}\n{snippet}\n"
    
    title = article.get('title', 'Testo personalizzato')
    summary = article.get('summary', '')
    author = article.get('author', 'Fonte sconosciuta')
    date = article.get('date', 'Data non disponibile')
    
    prompt = (
        f"Sei un analista di intelligence esperto con capacità di ragionamento complesso. Analizza la veridicità della seguente notizia usando un approccio step-by-step.\n\n"
        f"🔍 NOTIZIA DA VERIFICARE:\n"
        f"📰 Titolo: {title}\n"
        f"📝 Riassunto: {summary}\n"
        f"🏢 Fonte: {author}\n"
        f"📅 Data: {date}\n\n"
        f"🔎 FONTI DISPONIBILI:\n{fact_check_content}\n\n"
        f"✅ FONTI AFFIDABILI:\n{reliable_content}\n\n"
        f"🧠 RAGIONAMENTO STEP-BY-STEP:\n\n"
        f"**STEP 1: ANALISI INIZIALE**\n"
        f"Pensa ad alta voce:\n"
        f"- Quali sono gli elementi principali della notizia?\n"
        f"- Che tipo di affermazioni contiene (fatti, opinioni, interpretazioni)?\n"
        f"- Quali sono i potenziali punti di verifica?\n\n"
        f"**STEP 2: VALUTAZIONE DELLE FONTI**\n"
        f"Analizza criticamente:\n"
        f"- Quali fonti sono più affidabili e perché?\n"
        f"- Ci sono conflitti di interesse evidenti?\n"
        f"- Le fonti sono indipendenti tra loro?\n"
        f"- Ci sono bias temporali o geografici?\n\n"
        f"**STEP 3: VERIFICA INCROCIATA**\n"
        f"Confronta sistematicamente:\n"
        f"- Quali elementi sono confermati da più fonti?\n"
        f"- Ci sono contraddizioni tra le fonti?\n"
        f"- Le informazioni sono coerenti temporalmente?\n"
        f"- Ci sono anomalie o pattern sospetti?\n\n"
        f"**STEP 4: ANALISI DELLE EVIDENZE**\n"
        f"Valuta la qualità CRITICAMENTE:\n"
        f"- Quali sono le evidenze più forti?\n"
        f"- Per ogni studio scientifico: valuta metodologia, campione, peer review\n"
        f"- Le evidenze sono dirette o indirette?\n"
        f"- Ci sono gap informativi significativi?\n"
        f"- CHI ha finanziato lo studio? Ci sono conflitti di interesse?\n"
        f"- Esistono critiche o repliche dello studio specifico?\n"
        f"- Il consenso scientifico sul tema supporta o contraddice?\n\n"
        f"**STEP 5: VALUTAZIONE CRITICA DEGLI STUDI**\n"
        f"Analizza ogni studio scientifico:\n"
        f"- Metodologia: campione rappresentativo? controlli adeguati?\n"
        f"- Peer review: rivista di qualità? processo di revisione?\n"
        f"- Finanziamenti: chi ha pagato? conflitti di interesse?\n"
        f"- Critiche: esistono repliche o critiche metodologiche?\n"
        f"- Consenso: altri studi concordano o contraddicono?\n"
        f"- Predatory journals: rivista sconosciuta o di bassa qualità?\n"
        f"- Pattern sospetti: manipolazioni, contraddizioni, bias evidenti?\n\n"
        f"**STEP 6: VALUTAZIONE FINALE**\n"
        f"Raggiungi una conclusione:\n"
        f"- Basandoti su tutti gli step precedenti\n"
        f"- Considerando il livello di confidenza\n"
        f"- Identificando le limitazioni dell'analisi\n\n"
        f"🎯 RISULTATO FINALE:\n"
        f"1. **VERDETTO**: [VERA] / [FALSA] / [DUBBIA] / [INSUFFICIENTI DATI]\n"
        f"2. **LIVELLO DI CONFIDENZA**: [ALTO 90%+] / [MEDIO 70-90%] / [BASSO <70%]\n"
        f"3. **EVIDENZE CHIAVE**: Le prove più importanti\n"
        f"4. **RED FLAG IDENTIFICATI**: Segnali di allarme trovati\n"
        f"5. **LIMITAZIONI**: Cosa non possiamo sapere con certezza\n"
        f"6. **MOTIVAZIONE**: Spiega il ragionamento finale\n\n"
        f"⚠️ IMPORTANTE: \n"
        f"- Usa il ragionamento step-by-step per arrivare a conclusioni ben fondate\n"
        f"- VALUTA ogni studio scientifico individualmente (metodologia, qualità, consenso)\n"
        f"- Cerca CHI ha finanziato lo studio e eventuali conflitti di interesse\n"
        f"- Verifica se esistono critiche o repliche dello studio specifico\n"
        f"- Controlla il consenso scientifico sul tema\n"
        f"- Distingui tra studi di qualità e predatory journals\n\n"
        f"🌐 Se trovi contenuti in inglese, traduci automaticamente le informazioni chiave.\n\n"
        f"Rispondi in italiano con un ragionamento strutturato e dettagliato."
    )
    
    return ai_provider.generate(prompt, max_tokens=1500)

def agent_validazione_verita_advanced(article, verification_data, ai_provider):
    """Agente di validazione verità con ragionamento complesso step-by-step"""
    fact_check_results = verification_data.get('fact_check_results', [])
    reliable_results = verification_data.get('reliable_sources_results', [])
    
    fact_check_content = ""
    if fact_check_results and not fact_check_results[0].get('error'):
        for result in fact_check_results[:5]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            search_query = result.get('search_query', '')
            language = result.get('language', 'it')
            
            if language == 'en':
                title = f"[TRADOTTO] {title}"
                if full_content:
                    full_content = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {full_content}"
                else:
                    snippet = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {snippet}"
            
            if full_content:
                fact_check_content += f"\n--- FACT-CHECK: {title} ({source}) ---\nQuery: {search_query}\n{full_content}\n"
            else:
                fact_check_content += f"\n--- FACT-CHECK: {title} ({source}) ---\nQuery: {search_query}\n{snippet}\n"
    
    reliable_content = ""
    if reliable_results and not reliable_results[0].get('error'):
        for result in reliable_results[:5]:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            full_content = result.get('full_content', '')
            source = result.get('source', '')
            search_query = result.get('search_query', '')
            language = result.get('language', 'it')
            
            if language == 'en':
                title = f"[TRADOTTO] {title}"
                if full_content:
                    full_content = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {full_content}"
                else:
                    snippet = f"[CONTENUTO IN INGLESE - TRADUCI AUTOMATICAMENTE] {snippet}"
            
            if full_content:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\nQuery: {search_query}\n{full_content}\n"
            else:
                reliable_content += f"\n--- FONTE AFFIDABILE: {title} ({source}) ---\nQuery: {search_query}\n{snippet}\n"
    
    title = article.get('title', 'Testo personalizzato')
    summary = article.get('summary', '')
    author = article.get('author', 'Fonte sconosciuta')
    date = article.get('date', 'Data non disponibile')
    
    prompt = (
        f"Sei un analista di intelligence esperto. Valuta la veridicità di questa notizia usando un ragionamento step-by-step approfondito.\n\n"
        f"🔍 NOTIZIA DA VALIDARE:\n"
        f"📰 Titolo: {title}\n"
        f"📝 Riassunto: {summary}\n"
        f"🏢 Fonte: {author}\n"
        f"📅 Data: {date}\n\n"
        f"🔎 FONTI DISPONIBILI:\n{fact_check_content}\n\n"
        f"✅ FONTI AFFIDABILI:\n{reliable_content}\n\n"
        f"🧠 RAGIONAMENTO STRUTTURATO:\n\n"
        f"**STEP 1: DECOMPOSIZIONE DEL PROBLEMA**\n"
        f"Pensa ad alta voce:\n"
        f"- Quali sono le affermazioni specifiche da verificare?\n"
        f"- Che tipo di evidenze servirebbero per confermare/smentire?\n"
        f"- Quali sono i potenziali bias o limitazioni?\n\n"
        f"**STEP 2: VALUTAZIONE DELLE EVIDENZE**\n"
        f"Analizza sistematicamente:\n"
        f"- Quali evidenze supportano la notizia?\n"
        f"- Quali evidenze la contraddicono?\n"
        f"- Quali sono le evidenze più affidabili?\n"
        f"- Per ogni studio scientifico: valuta metodologia, campione, peer review\n"
        f"- Ci sono evidenze 'sospette' o di parte?\n"
        f"- CHI ha finanziato la ricerca? Ci sono conflitti di interesse?\n"
        f"- Esistono critiche o repliche dello studio specifico?\n"
        f"- Il consenso scientifico sul tema supporta o contraddice?\n\n"
        f"**STEP 3: ANALISI DELLE FONTI**\n"
        f"Valuta criticamente:\n"
        f"- Quali fonti sono più credibili?\n"
        f"- Ci sono conflitti di interesse?\n"
        f"- Le fonti sono indipendenti?\n"
        f"- Ci sono pattern di bias?\n\n"
        f"**STEP 4: VALUTAZIONE CRITICA DEGLI STUDI**\n"
        f"Analizza ogni studio scientifico:\n"
        f"- Metodologia: campione rappresentativo? controlli adeguati?\n"
        f"- Peer review: rivista di qualità? processo di revisione?\n"
        f"- Finanziamenti: chi ha pagato? conflitti di interesse?\n"
        f"- Critiche: esistono repliche o critiche metodologiche?\n"
        f"- Consenso: altri studi concordano o contraddicono?\n"
        f"- Predatory journals: rivista sconosciuta o di bassa qualità?\n"
        f"- Contraddizioni temporali o logiche?\n"
        f"- Pattern sospetti o manipolazioni evidenti?\n\n"
        f"**STEP 5: VALUTAZIONE DELLA CONFIDENZA**\n"
        f"Determina il livello di certezza:\n"
        f"- Quanto sono forti le evidenze?\n"
        f"- Quanto sono affidabili le fonti?\n"
        f"- Ci sono gap informativi?\n"
        f"- Quali sono le incertezze?\n\n"
        f"**STEP 6: CONCLUSIONE FINALE**\n"
        f"Raggiungi un verdetto:\n"
        f"- Basandoti su tutti gli step precedenti\n"
        f"- Considerando il livello di confidenza\n"
        f"- Identificando le limitazioni\n\n"
        f"🎯 VERDETTO FINALE:\n"
        f"1. **VERDETTO**: [VERA] / [FALSA] / [DUBBIA] / [INSUFFICIENTI DATI]\n"
        f"2. **CONFIDENZA**: [ALTO 90%+] / [MEDIO 70-90%] / [BASSO <70%]\n"
        f"3. **EVIDENZE CHIAVE**: Le prove più importanti\n"
        f"4. **RED FLAG**: Segnali di allarme identificati\n"
        f"5. **LIMITAZIONI**: Cosa non possiamo sapere\n"
        f"6. **MOTIVAZIONE**: Spiega il ragionamento finale\n\n"
        f"⚠️ IMPORTANTE: \n"
        f"- Usa il ragionamento step-by-step per conclusioni ben fondate\n"
        f"- VALUTA ogni studio scientifico individualmente (metodologia, qualità, consenso)\n"
        f"- Cerca CHI ha finanziato lo studio e eventuali conflitti di interesse\n"
        f"- Verifica se esistono critiche o repliche dello studio specifico\n"
        f"- Controlla il consenso scientifico sul tema\n"
        f"- Distingui tra studi di qualità e predatory journals\n\n"
        f"🌐 Se trovi contenuti in inglese, traduci automaticamente.\n\n"
        f"Rispondi in italiano con un ragionamento strutturato e dettagliato."
    )
    
    return ai_provider.generate(prompt, max_tokens=1200)
