#!/usr/bin/env python

import requests
import json
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re

class NewsVerifier:
    def __init__(self, serpapi_key: str):
        self.serpapi_key = serpapi_key
        self.base_url = "https://serpapi.com/search"
    
    def scrape_article_content(self, url: str) -> str:
        """Scarica e estrae il contenuto dell'articolo dal link"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Gestione encoding migliorata
            if response.encoding == 'ISO-8859-1':
                response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)
            
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # Cerca il contenuto principale
            content_selectors = [
                'article',
                '[class*="content"]',
                '[class*="article"]',
                '[class*="post"]',
                '.entry-content',
                '.post-content',
                '.article-content',
                'main'
            ]
            
            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text(strip=True) for elem in elements])
                    if len(content) > 200:
                        break
            
            if not content or len(content) < 200:
                body = soup.find('body')
                if body:
                    content = body.get_text(strip=True)
            
            content = re.sub(r'\s+', ' ', content)
            # Pulizia più robusta dei caratteri problematici
            content = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\'\"àèéìòùÀÈÉÌÒÙ]', '', content)
            # Rimuovi caratteri di controllo
            content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\t')
            
            if len(content) > 3000:
                content = content[:3000] + "..."
            
            return content
            
        except Exception as e:
            return None
    
    def analyze_content_for_languages(self, content: str) -> list:
        """Analizza il contenuto per determinare le lingue più appropriate per la ricerca"""
        # Lingue supportate con i loro identificatori
        supported_languages = {
            'it': {'name': 'Italiano', 'gl': 'it', 'hl': 'it'},
            'en': {'name': 'Inglese', 'gl': 'us', 'hl': 'en'},
            'fr': {'name': 'Francese', 'gl': 'fr', 'hl': 'fr'},
            'de': {'name': 'Tedesco', 'gl': 'de', 'hl': 'de'},
            'es': {'name': 'Spagnolo', 'gl': 'es', 'hl': 'es'},
            'pt': {'name': 'Portoghese', 'gl': 'pt', 'hl': 'pt'},
            'ru': {'name': 'Russo', 'gl': 'ru', 'hl': 'ru'},
            'zh': {'name': 'Cinese', 'gl': 'cn', 'hl': 'zh-cn'},
            'ja': {'name': 'Giapponese', 'gl': 'jp', 'hl': 'ja'},
            'ar': {'name': 'Arabo', 'gl': 'sa', 'hl': 'ar'}
        }
        
        # Analisi semantica del contenuto per determinare le lingue
        content_lower = content.lower()
        
        # Regole per determinare le lingue appropriate
        languages_to_search = ['it']  # Italiano sempre incluso
        
        # Rileva eventi internazionali
        international_keywords = [
            'united states', 'usa', 'america', 'biden', 'trump', 'white house',
            'france', 'francia', 'francese', 'macron', 'paris', 'parigi',
            'germany', 'germania', 'tedesco', 'merkel', 'berlin', 'berlino',
            'spain', 'spagna', 'spagnolo', 'madrid', 'barcelona', 'barcellona',
            'portugal', 'portogallo', 'portoghese', 'lisbon', 'lisbona',
            'russia', 'russia', 'russo', 'putin', 'moscow', 'mosca',
            'china', 'cina', 'cinese', 'beijing', 'pechino', 'shanghai',
            'japan', 'giappone', 'giapponese', 'tokyo', 'tokyo', 'osaka',
            'arab', 'arabo', 'middle east', 'medio oriente', 'dubai',
            'un', 'nato', 'eu', 'european union', 'unione europea', 'who', 'imf', 'world bank'
        ]
        
        # Rileva argomenti tecnici/scientifici (solitamente meglio in inglese)
        technical_keywords = [
            'technology', 'ai', 'artificial intelligence', 'machine learning',
            'blockchain', 'cryptocurrency', 'space', 'nasa', 'satellite',
            'medical', 'vaccine', 'clinical trial', 'research', 'study',
            'financial', 'stock market', 'cryptocurrency', 'bitcoin'
        ]
        
        # Rileva eventi sportivi internazionali
        sports_keywords = [
            'champions league', 'premier league', 'la liga', 'bundesliga',
            'world cup', 'olympics', 'fifa', 'uefa', 'nba', 'nfl'
        ]
        
        # Determina le lingue da usare
        if any(keyword in content_lower for keyword in international_keywords):
            languages_to_search.extend(['en', 'fr', 'de', 'es'])
        
        if any(keyword in content_lower for keyword in technical_keywords):
            languages_to_search.append('en')
        
        if any(keyword in content_lower for keyword in sports_keywords):
            languages_to_search.extend(['en', 'es', 'pt'])
        
        # Rimuovi duplicati e mantieni solo le prime 3 lingue per efficienza
        languages_to_search = list(dict.fromkeys(languages_to_search))[:3]
        
        # Debug: mostra cosa ha rilevato
        detected_keywords = []
        for keyword in international_keywords:
            if keyword in content_lower:
                detected_keywords.append(keyword)
        
        if detected_keywords:
            print(f"🔍 Keywords internazionali rilevate: {', '.join(detected_keywords)}")
        else:
            print(f"🔍 Nessuna keyword internazionale rilevata in: {content_lower[:100]}...")
        
        return [supported_languages[lang] for lang in languages_to_search if lang in supported_languages]
    
    def _create_smart_query(self, title: str, summary: str) -> str:
        """Crea una query intelligente usando un LLM"""
        try:
            from .ai_providers import create_ai_provider
            from .settings import load_settings
            
            settings = load_settings()
            provider = settings.get('provider', 'auto')
            ai_provider = create_ai_provider(provider, settings)
            
            prompt = f"""
            Crea 3 query di ricerca Google ottimali per verificare questa notizia.
            
            TITOLO: {title}
            RIASSUNTO: {summary}
            
            REGOLE:
            1. Ogni query deve essere di 2-5 parole chiave
            2. Includi sempre il paese/regione se menzionato
            3. Usa termini generici ma specifici
            4. Evita articoli, preposizioni, congiunzioni
            5. Focalizzati sui fatti principali
            
            ESEMPI:
            - "incendi francia aude" (non "incendi nel dipartimento dell'aude")
            - "terremoto turchia siria" (non "terremoto devastante in turchia e siria")
            - "elezioni italia 2024" (non "elezioni politiche italiane del 2024")
            
            FORMATO RISPOSTA:
            QUERY1: [prima query]
            QUERY2: [seconda query] 
            QUERY3: [terza query]
            """
            
            response = ai_provider.generate(prompt, max_tokens=100)
            
            # Estrai la prima query
            lines = response.split('\n')
            for line in lines:
                if line.startswith('QUERY1:'):
                    query = line.replace('QUERY1:', '').strip()
                    # Rimuovi le virgolette se presenti
                    query = query.strip('"').strip("'")
                    return query
            
            # Fallback se non riesce a estrarre
            return self._create_simple_query(title, summary)
            
        except Exception as e:
            print(f"⚠️ Errore creazione query LLM: {e}")
            return self._create_simple_query(title, summary)
    
    def _create_simple_query(self, title: str, summary: str) -> str:
        """Fallback: crea query semplice senza LLM"""
        import re
        
        # Combina titolo e summary
        text = f"{title} {summary}"
        
        # Rimuovi caratteri speciali e normalizza
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Parole da rimuovere (stop words)
        stop_words = {
            'il', 'la', 'lo', 'le', 'gli', 'un', 'una', 'uno', 'e', 'o', 'ma', 'per', 'con', 'su', 'da', 'di', 'a', 'in', 'tra', 'fra',
            'che', 'chi', 'cui', 'quale', 'quali', 'quanto', 'quanta', 'quanti', 'quante', 'come', 'dove', 'quando', 'perché',
            'questo', 'questa', 'questi', 'queste', 'quello', 'quella', 'quelli', 'quelle', 'mio', 'mia', 'miei', 'mie', 'tuo', 'tua', 'tuoi', 'tue',
            'suo', 'sua', 'suoi', 'sue', 'nostro', 'nostra', 'nostri', 'nostre', 'vostro', 'vostra', 'vostri', 'vostre',
            'essere', 'stare', 'avere', 'fare', 'dire', 'andare', 'venire', 'vedere', 'sapere', 'potere', 'volere', 'dovere',
            'nel', 'nella', 'nello', 'nelle', 'negli', 'dal', 'dalla', 'dallo', 'dalle', 'dagli', 'al', 'alla', 'allo', 'alle', 'agli',
            'del', 'della', 'dello', 'delle', 'degli', 'col', 'colla', 'collo', 'colle', 'cogli', 'sul', 'sulla', 'sullo', 'sulle', 'sugli'
        }
        
        # Estrai parole significative
        words = text.split()
        keywords = []
        
        for word in words:
            if len(word) > 2 and word not in stop_words:
                keywords.append(word)
        
        # Prendi le prime 5-8 parole più significative
        keywords = keywords[:8]
        
        # Crea query
        query = ' '.join(keywords)
        
        return query
    
    def search_fact_check(self, query, mode="media", content=""):
        """Cerca articoli di fact-checking sulla query con ricerca intelligente multilingue"""
        # Determina le lingue da usare
        languages_to_search = self.analyze_content_for_languages(content) if content else [
            {'name': 'Italiano', 'gl': 'it', 'hl': 'it'},
            {'name': 'Inglese', 'gl': 'us', 'hl': 'en'}
        ]
        
        print(f"🌐 Ricerca intelligente in: {', '.join([lang['name'] for lang in languages_to_search])}")
        
        # Configurazione basata sulla modalità
        if mode == "veloce":
            max_queries_per_lang = 2
            max_results = 5
            max_languages = 2
        elif mode == "media":
            max_queries_per_lang = 3
            max_results = 10
            max_languages = 3
        elif mode == "grande":
            max_queries_per_lang = 5
            max_results = 15
            max_languages = 4
        else:
            max_queries_per_lang = 3
            max_results = 10
            max_languages = 3
        
        # Limita il numero di lingue per efficienza
        languages_to_search = languages_to_search[:max_languages]

        # Query per fact-checking in diverse lingue (ridotte)
        fact_check_queries = {
            'it': [
                f'"{query}" fact check',
                f'"{query}" fake news'
            ],
            'en': [
                f'"{query}" fact check',
                f'"{query}" fake news'
            ],
            'fr': [
                f'"{query}" fact check',
                f'"{query}" fake news'
            ],
            'de': [
                f'"{query}" fact check',
                f'"{query}" fake news'
            ],
            'es': [
                f'"{query}" fact check',
                f'"{query}" fake news'
            ]
        }
        
        all_results = []
        
        # Esegue ricerche in tutte le lingue determinate
        for lang_config in languages_to_search:
            # Se abbiamo già abbastanza risultati, fermati
            if len(all_results) >= max_results:
                break
                
            lang_code = next(k for k, v in {'it': 'it', 'en': 'en', 'fr': 'fr', 'de': 'de', 'es': 'es'}.items() 
                           if v == lang_config['hl'])
            
            queries = fact_check_queries.get(lang_code, fact_check_queries['en'])[:max_queries_per_lang]
            
            for search_query in queries:
                # Se abbiamo già abbastanza risultati, fermati
                if len(all_results) >= max_results:
                    break
                try:
                    params = {
                        'api_key': self.serpapi_key,
                        'engine': 'google',
                        'q': search_query,
                        'num': 3 if mode == "veloce" else 5,
                        'gl': lang_config['gl'],
                        'hl': lang_config['hl']
                    }
                    
                    response = requests.get('https://serpapi.com/search', params=params, timeout=10)
                    data = response.json()
                    
                    print(f"🔍 SerpAPI fact-check '{search_query}' ({lang_config['name']}): {len(data.get('organic_results', []))} risultati")
                    
                    if 'organic_results' in data:
                        for result in data['organic_results']:
                            full_content = self.scrape_article_content(result.get('link', '')) if mode != "veloce" else ""
                            
                            all_results.append({
                                'title': result.get('title', ''),
                                'link': result.get('link', ''),
                                'snippet': result.get('snippet', ''),
                                'source': result.get('source', ''),
                                'full_content': full_content,
                                'search_query': search_query,
                                'language': lang_code
                            })
                            
                except Exception as e:
                    print(f"Errore ricerca fact-check {lang_config['name']}: {e}")
                    continue
        
        return all_results[:max_results]

    def search_reliable_sources(self, query, mode="media", content=""):
        """Cerca fonti affidabili sulla query con ricerca intelligente multilingue"""
        # Determina le lingue da usare
        languages_to_search = self.analyze_content_for_languages(content) if content else [
            {'name': 'Italiano', 'gl': 'it', 'hl': 'it'},
            {'name': 'Inglese', 'gl': 'us', 'hl': 'en'}
        ]
        
        print(f"🌐 Ricerca fonti affidabili in: {', '.join([lang['name'] for lang in languages_to_search])}")
        
        # Configurazione basata sulla modalità
        if mode == "veloce":
            max_queries_per_lang = 2
            max_results = 5
            max_languages = 2
        elif mode == "media":
            max_queries_per_lang = 3
            max_results = 10
            max_languages = 3
        elif mode == "grande":
            max_queries_per_lang = 5
            max_results = 15
            max_languages = 4
        else:
            max_queries_per_lang = 3
            max_results = 10
            max_languages = 3
        
        # Limita il numero di lingue per efficienza
        languages_to_search = languages_to_search[:max_languages]
        
        # Query per fonti affidabili in diverse lingue (ridotte)
        reliable_queries = {
            'it': [
                f'"{query}"',
                f'"{query}" inchiesta'
            ],
            'en': [
                f'"{query}"',
                f'"{query}" investigation'
            ],
            'fr': [
                f'"{query}"',
                f'"{query}" enquête'
            ],
            'de': [
                f'"{query}"',
                f'"{query}" untersuchung'
            ],
            'es': [
                f'"{query}"',
                f'"{query}" investigación'
            ]
        }
        
        # Fonti affidabili per lingua
        reliable_sources = {
            'it': [
                'ansa.it', 'corriere.it', 'repubblica.it', 'ilsole24ore.com',
                'ilfattoquotidiano.it', 'rainews.it', 'tg24.sky.it', 'adnkronos.com',
                'agi.it', 'askanews.it', 'ilgiornale.it', 'ilpost.it',
                'internazionale.it', 'espresso.repubblica.it',
                'panorama.it', 'ilfoglio.it', 'ilmanifesto.it'
            ],
            'en': [
                'reuters.com', 'ap.org', 'bbc.com', 'theguardian.com',
                'nytimes.com', 'washingtonpost.com', 'cnn.com', 'nbcnews.com',
                'abcnews.go.com', 'cbsnews.com', 'npr.org',
                'nature.com', 'science.org', 'who.int', 'nasa.gov',
                'mit.edu', 'harvard.edu', 'stanford.edu', 'un.org'
            ],
            'fr': [
                'lemonde.fr', 'lefigaro.fr', 'liberation.fr', 'lepoint.fr',
                'lexpress.fr', 'nouvelobs.com', 'france24.com', 'rfi.fr'
            ],
            'de': [
                'spiegel.de', 'zeit.de', 'faz.net', 'sueddeutsche.de',
                'welt.de', 'tagesschau.de', 'ard.de', 'zdf.de'
            ],
            'es': [
                'elpais.com', 'elmundo.es', 'abc.es', 'lavanguardia.com',
                'elperiodico.com', '20minutos.es', 'rtve.es'
            ]
        }
        
        all_results = []
        
        # Esegue ricerche in tutte le lingue determinate
        for lang_config in languages_to_search:
            lang_code = next(k for k, v in {'it': 'it', 'en': 'en', 'fr': 'fr', 'de': 'de', 'es': 'es'}.items() 
                           if v == lang_config['hl'])
            
            queries = reliable_queries.get(lang_code, reliable_queries['en'])[:max_queries_per_lang]
            sources = reliable_sources.get(lang_code, reliable_sources['en'])
            
            for search_query in queries:
                try:
                    params = {
                        'api_key': self.serpapi_key,
                        'engine': 'google',
                        'q': search_query,
                        'num': 3 if mode == "veloce" else 5,
                        'gl': lang_config['gl'],
                        'hl': lang_config['hl']
                    }
                    
                    response = requests.get('https://serpapi.com/search', params=params, timeout=10)
                    data = response.json()
                    
                    print(f"🔍 SerpAPI fonti affidabili '{search_query}' ({lang_config['name']}): {len(data.get('organic_results', []))} risultati")
                    
                    if 'organic_results' in data:
                        for result in data['organic_results']:
                            link = result.get('link', '').lower()
                            if any(source in link for source in sources):
                                full_content = self.scrape_article_content(result.get('link', '')) if mode != "veloce" else ""
                                
                                all_results.append({
                                    'title': result.get('title', ''),
                                    'link': result.get('link', ''),
                                    'snippet': result.get('snippet', ''),
                                    'source': result.get('source', ''),
                                    'full_content': full_content,
                                    'search_query': search_query,
                                    'language': lang_code
                                })
                                
                except Exception as e:
                    print(f"Errore ricerca fonti affidabili {lang_config['name']}: {e}")
                    continue
        
        return all_results[:max_results]
    
    def verify_article(self, article: Dict, mode: str = "media") -> Dict:
        """Verifica un articolo completo"""
        title = article.get('title', '')
        summary = article.get('summary', '')
        content = article.get('content', '') or summary
        
        # Crea query più intelligenti
        query = self._create_smart_query(title, summary)
        
        print(f"🔍 Query di ricerca: {query}")
        print(f"📄 Contenuto analizzato: {content[:200]}...")
        
        # Analizza titolo + contenuto per le lingue
        full_content_for_languages = f"{title} {content}"
        
        fact_check_results = self.search_fact_check(query, mode, full_content_for_languages)
        reliable_results = self.search_reliable_sources(query, mode, full_content_for_languages)
        
        print(f"📊 Risultati fact-check: {len(fact_check_results)}")
        print(f"📰 Risultati fonti affidabili: {len(reliable_results)}")
        
        return {
            'article': article,
            'fact_check_results': fact_check_results,
            'reliable_sources_results': reliable_results,
            'verification_summary': self._generate_verification_summary(
                fact_check_results, reliable_results, title
            )
        }
    
    def verify_text(self, text: str, mode: str = "media") -> Dict:
        """Verifica un testo personalizzato"""
        # Crea query intelligente dal testo
        query = self._create_smart_query(text, "")
        
        fact_check_results = self.search_fact_check(query, mode, text)
        reliable_results = self.search_reliable_sources(query, mode, text)
        
        return {
            'text': text,
            'fact_check_results': fact_check_results,
            'reliable_sources_results': reliable_results,
            'verification_summary': self._generate_verification_summary(
                fact_check_results, reliable_results, text
            )
        }
    
    def verify_truthfulness(self, article: Dict) -> Dict:
        """Verifica la veridicità di un articolo (alias di verify_article per la validazione della verità)"""
        return self.verify_article(article)
    
    def _generate_verification_summary(self, fact_check_results: List[Dict], 
                                     reliable_results: List[Dict], 
                                     query: str) -> str:
        """Genera un riassunto della verifica"""
        if not fact_check_results and not reliable_results:
            return "Nessuna informazione di verifica trovata."
        
        summary_parts = []
        
        if fact_check_results and not fact_check_results[0].get('error'):
            summary_parts.append("🔍 FACT-CHECKING:")
            for i, result in enumerate(fact_check_results[:3], 1):
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                source = result.get('source', '')
                has_full_content = "✅" if result.get('full_content') else "⚠️"
                summary_parts.append(f"  {i}. {title} ({source}) {has_full_content}")
                if result.get('full_content'):
                    summary_parts.append(f"     Contenuto completo scaricato ({len(result['full_content'])} caratteri)")
                else:
                    summary_parts.append(f"     {snippet[:150]}...")

        if reliable_results and not reliable_results[0].get('error'):
            summary_parts.append("\n📰 FONTI AFFIDABILI:")
            for i, result in enumerate(reliable_results[:3], 1):
                title = result.get('title', '')
                source = result.get('source', '')
                has_full_content = "✅" if result.get('full_content') else "⚠️"
                summary_parts.append(f"  {i}. {title} ({source}) {has_full_content}")
                if result.get('full_content'):
                    summary_parts.append(f"     Contenuto completo scaricato ({len(result['full_content'])} caratteri)")

        summary_parts.append("\n📊 VALUTAZIONE:")
        if fact_check_results and not fact_check_results[0].get('error'):
            summary_parts.append("✅ Informazioni di fact-checking disponibili")
        else:
            summary_parts.append("⚠️ Nessun fact-check specifico trovato")
        
        if reliable_results and not reliable_results[0].get('error'):
            summary_parts.append("✅ Fonti affidabili hanno coperto l'argomento")
        else:
            summary_parts.append("⚠️ Poche fonti affidabili trovate")
        
        return "\n".join(summary_parts) 