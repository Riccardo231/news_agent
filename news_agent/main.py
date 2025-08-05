#!/usr/bin/env python

from .settings import load_settings
from .fetcher import fetch_articles
from .agents import agent_riassunto, agent_implicazioni, agent_teoria, agent_verifica, agent_analisi_universale, summarize_with_ollama
from .ui import show_table, show_article, show_verification_menu, show_verification_results, get_custom_text, get_arrow_input
from .verifier import NewsVerifier
from rich.panel import Panel
from rich.console import Console
import webbrowser
import sys

def main():
    settings = load_settings()
    lang = settings.get("lang", "it")
    topic = settings.get("topic")
    per_page = int(settings.get("articles_per_page", 15))
    model = settings.get("model", "qwen2:7b-instruct")
    ollama_url = settings.get("ollama_url", "http://localhost:11434/api/generate")
    serpapi_key = settings.get("serpapi_key", "").strip()
    
    verifier = None
    if serpapi_key:
        try:
            verifier = NewsVerifier(serpapi_key)
            console = Console()
            console.print("[green]✅ SerpAPI configurato - Funzione verifica disponibile[/green]")
        except Exception as e:
            console = Console()
            console.print(f"[red]❌ Errore nell'inizializzazione di SerpAPI: {e}[/red]")
            verifier = None
    
    feed = f"https://news.google.com/rss?hl={lang}&gl={lang.upper()}&ceid={topic or ''}"
    articles = fetch_articles(feed)
    if not articles:
        print("Nessun articolo trovato!")
        return
    
    console = Console()
    current_page = 1
    total_pages = (len(articles) + per_page - 1) // per_page
    selected_idx = 0

    while True:
        show_table(articles, current_page, per_page, selected_idx, has_serpapi=verifier is not None)
        user_input = get_arrow_input()

        if user_input == 'q':
            break
        elif user_input in ['n', 'avanti'] and current_page < total_pages:
            current_page += 1
        elif user_input in ['p', 'indietro'] and current_page > 1:
            current_page -= 1
        elif user_input in ['up', 'w'] and selected_idx > 0:
            selected_idx -= 1
        elif user_input in ['down', 'z'] and selected_idx < len(articles) - 1:
            selected_idx += 1
        elif user_input == 'f':
            # Passa alle notizie successive
            if selected_idx < len(articles) - 1:
                selected_idx += 1
            elif current_page < total_pages:
                current_page += 1
                selected_idx = 0
            else:
                console.print("[yellow]Sei già all'ultima notizia![/yellow]")
        elif user_input == 's':
            summary = summarize_with_ollama(articles, model, ollama_url)
            console.print(Panel(summary, title="Sunto globale delle notizie", border_style="cyan"))
            console.input("\nPremi invio per tornare alla lista")
        elif user_input == 'o':
            idx = selected_idx
            webbrowser.open(articles[idx]['link'])
            console.print(f"[bold green]Apro la notizia #{idx} nel browser...[/bold green]")
        elif user_input == 'a':
            handle_agents_menu(articles, selected_idx, model, ollama_url, console)
        elif user_input == 'v' and verifier:
            handle_verification(verifier, articles, selected_idx, model, ollama_url, console)
        elif user_input == '\r' or user_input == '\n':
            show_article(articles[selected_idx])
            console.input("Premi invio per tornare alla lista: ")
        else:
            try:
                idx = int(user_input)
                if 0 <= idx < len(articles):
                    selected_idx = idx
                    show_article(articles[idx])
                    console.input("Premi invio per tornare alla lista: ")
            except ValueError:
                console.print("[red]Input non valido, riprova.[/red]")

def handle_agents_menu(articles, selected_idx, model, ollama_url, console):
    """Gestisce il menu degli agenti LLM"""
    article = articles[selected_idx]
    show_article(article)
    
    console.print("\n[bold cyan]🤖 MENU AGENTI LLM[/bold cyan]")
    console.print("1. Riassunto (Agente 1)")
    console.print("2. Implicazioni (Agente 2)")
    console.print("3. Teoria/Scenario (Agente 3)")
    console.print("4. Analisi Universale (Framework Multi-tematico)")
    console.print("5. Tutti gli agenti in sequenza")
    console.print("0. Torna indietro")
    
    choice = console.input("\nSeleziona agente (0-5): ").strip()
    
    if choice == '1':
        console.print("\n[bold yellow]1. Riassunto (Agente 1)...[/bold yellow]")
        riassunto = agent_riassunto(article, model, ollama_url)
        console.print(Panel(riassunto, title="Riassunto", border_style="yellow"))
        console.input("\nPremi invio per tornare alla lista")
        
    elif choice == '2':
        console.print("\n[bold cyan]2. Implicazioni (Agente 2)...[/bold cyan]")
        riassunto = agent_riassunto(article, model, ollama_url)
        implicazioni = agent_implicazioni(article, riassunto, model, ollama_url)
        console.print(Panel(implicazioni, title="Implicazioni", border_style="cyan"))
        console.input("\nPremi invio per tornare alla lista")
        
    elif choice == '3':
        console.print("\n[bold magenta]3. Teoria/Scenario (Agente 3)...[/bold magenta]")
        riassunto = agent_riassunto(article, model, ollama_url)
        implicazioni = agent_implicazioni(article, riassunto, model, ollama_url)
        teoria = agent_teoria(article, riassunto, implicazioni, model, ollama_url)
        console.print(Panel(teoria, title="Teoria/Scenario", border_style="magenta"))
        console.input("\nPremi invio per tornare alla lista")
        
    elif choice == '4':
        console.print("\n[bold green]4. Analisi Universale (Framework Multi-tematico)...[/bold green]")
        console.print("[dim]Questo agente usa un framework metodologico universale per analisi complesse[/dim]")
        analisi = agent_analisi_universale(article, model, ollama_url)
        console.print(Panel(analisi, title="Analisi Universale - Framework Multi-tematico", border_style="green"))
        console.input("\nPremi invio per tornare alla lista")
        
    elif choice == '5':
        console.print("\n[bold yellow]1. Riassunto (Agente 1)...[/bold yellow]")
        riassunto = agent_riassunto(article, model, ollama_url)
        console.print(Panel(riassunto, title="Riassunto", border_style="yellow"))
        
        console.print("\n[bold cyan]2. Implicazioni (Agente 2)...[/bold cyan]")
        implicazioni = agent_implicazioni(article, riassunto, model, ollama_url)
        console.print(Panel(implicazioni, title="Implicazioni", border_style="cyan"))
        
        console.print("\n[bold magenta]3. Teoria/Scenario (Agente 3)...[/bold magenta]")
        teoria = agent_teoria(article, riassunto, implicazioni, model, ollama_url)
        console.print(Panel(teoria, title="Teoria/Scenario", border_style="magenta"))
        
        console.print("\n[bold green]4. Analisi Universale (Framework Multi-tematico)...[/bold green]")
        analisi = agent_analisi_universale(article, model, ollama_url)
        console.print(Panel(analisi, title="Analisi Universale - Framework Multi-tematico", border_style="green"))
        
        console.input("\nPremi invio per tornare alla lista")

def handle_verification(verifier, articles, selected_idx, model, ollama_url, console):
    """Gestisce il menu di verifica e le relative operazioni"""
    while True:
        choice = show_verification_menu()
        
        if choice == '0':
            break
        elif choice == '1':
            article = articles[selected_idx]
            console.print(f"\n[bold yellow]🔍 Verificando: {article['title']}[/bold yellow]")
            
            try:
                verification_data = verifier.verify_article(article)
                
                console.print("\n[bold cyan]🤖 Analizzando con Agente LLM...[/bold cyan]")
                agent_analysis = agent_verifica(article, verification_data, model, ollama_url)
                
                show_verification_results(verification_data, agent_analysis)
            except Exception as e:
                console.print(f"[red]❌ Errore durante la verifica: {e}[/red]")
                console.input("\nPremi invio per continuare...")
                
        elif choice == '2':
            custom_text = get_custom_text()
            if custom_text.strip():
                console.print(f"\n[bold yellow]🔍 Verificando testo personalizzato...[/bold yellow]")
                
                try:
                    verification_data = verifier.verify_text(custom_text)
                    
                    fake_article = {
                        'title': 'Testo personalizzato',
                        'summary': custom_text,
                        'author': 'Utente',
                        'date': 'Oggi'
                    }
                    
                    console.print("\n[bold cyan]🤖 Analizzando con Agente LLM...[/bold cyan]")
                    agent_analysis = agent_verifica(fake_article, verification_data, model, ollama_url)
                    
                    show_verification_results(verification_data, agent_analysis)
                except Exception as e:
                    console.print(f"[red]❌ Errore durante la verifica: {e}[/red]")
                    console.input("\nPremi invio per continuare...")
            else:
                console.print("[yellow]Nessun testo inserito.[/yellow]")
                console.input("\nPremi invio per continuare...")
        else:
            console.print("[red]Opzione non valida.[/red]")
            console.input("\nPremi invio per continuare...")

if __name__ == "__main__":
    main()
