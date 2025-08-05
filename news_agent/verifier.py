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
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
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
            content = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\'\"]', '', content)
            
            if len(content) > 3000:
                content = content[:3000] + "..."
            
            return content
            
        except Exception as e:
            return None
    
    def search_fact_check(self, query: str, max_results: int = 5) -> List[Dict]:
        """Cerca informazioni di fact-checking su una query"""
        params = {
            'q': f"{query} fact check verification",
            'api_key': self.serpapi_key,
            'engine': 'google',
            'num': max_results,
            'gl': 'it',
            'hl': 'it'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'organic_results' in data:
                for result in data['organic_results']:
                    full_content = self.scrape_article_content(result.get('link', ''))
                    
                    results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'link': result.get('link', ''),
                        'source': result.get('source', ''),
                        'full_content': full_content
                    })
            
            return results
        except Exception as e:
            return [{'error': f"Errore nella ricerca: {str(e)}"}]
    
    def search_reliable_sources(self, query: str, max_results: int = 5) -> List[Dict]:
        """Cerca informazioni da fonti affidabili"""
        reliable_sources = [
            "reuters.com", "ap.org", "bbc.com", "corriere.it", 
            "repubblica.it", "ansa.it", "ilsole24ore.com"
        ]
        
        params = {
            'q': query,
            'api_key': self.serpapi_key,
            'engine': 'google',
            'num': max_results * 2,
            'gl': 'it',
            'hl': 'it'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'organic_results' in data:
                for result in data['organic_results']:
                    link = result.get('link', '').lower()
                    if any(source in link for source in reliable_sources):
                        full_content = self.scrape_article_content(result.get('link', ''))
                        
                        results.append({
                            'title': result.get('title', ''),
                            'snippet': result.get('snippet', ''),
                            'link': result.get('link', ''),
                            'source': result.get('source', ''),
                            'full_content': full_content
                        })
                        if len(results) >= max_results:
                            break
            
            return results
        except Exception as e:
            return [{'error': f"Errore nella ricerca: {str(e)}"}]
    
    def verify_article(self, article: Dict) -> Dict:
        """Verifica un articolo completo"""
        title = article.get('title', '')
        summary = article.get('summary', '')
        
        query = f"{title} {summary[:100]}"
        
        fact_check_results = self.search_fact_check(query)
        reliable_results = self.search_reliable_sources(query)
        
        return {
            'article': article,
            'fact_check_results': fact_check_results,
            'reliable_sources_results': reliable_results,
            'verification_summary': self._generate_verification_summary(
                fact_check_results, reliable_results, title
            )
        }
    
    def verify_text(self, text: str) -> Dict:
        """Verifica un testo personalizzato"""
        fact_check_results = self.search_fact_check(text)
        reliable_results = self.search_reliable_sources(text)
        
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