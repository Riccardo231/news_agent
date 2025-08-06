#!/usr/bin/env python

from .settings import load_settings
from .fetcher import fetch_articles
from .agents import agent_riassunto, agent_implicazioni, agent_teoria, summarize_article, agent_verifica, agent_validazione_verita, agent_verifica_advanced, agent_validazione_verita_advanced
from .multi_agents import run_multi_agent_verification
from .ui import show_table, show_article, get_arrow_input, show_verification_menu, show_verification_results, show_settings_menu, edit_ai_provider, edit_ai_model, edit_api_keys, edit_serpapi, edit_general_settings, show_current_settings, save_settings_change
from .ai_providers import create_ai_provider
from .verifier import NewsVerifier
from rich.panel import Panel
from rich.console import Console
import webbrowser
import sys

def get_model_name(ai_provider):
    """Ottiene il nome del modello dall'AI provider"""
    if hasattr(ai_provider, 'model'):
        return ai_provider.model
    return "Modello sconosciuto"

def handle_settings_menu(console):
    """Gestisce il menu delle impostazioni"""
    while True:
        choice = show_settings_menu()
        
        if choice == '0':
            break
        elif choice == '1':
            provider = edit_ai_provider()
            if provider and save_settings_change('provider', provider):
                console.print(f"[green]✅ Provider AI impostato su: {provider}[/green]")
                console.input("\nPremi invio per continuare...")
        elif choice == '2':
            from .settings import load_settings
            settings = load_settings()
            current_provider = settings.get('provider', 'ollama')
            
            if current_provider == 'auto':
                console.print("[yellow]⚠️ Impostazione 'auto' attiva. Seleziona prima un provider specifico.[/yellow]")
                console.input("\nPremi invio per continuare...")
                continue
            
            model = edit_ai_model(current_provider)
            if model:
                key = f'{current_provider}_model'
                if save_settings_change(key, model):
                    console.print(f"[green]✅ Modello {current_provider} impostato su: {model}[/green]")
                    console.input("\nPremi invio per continuare...")
        elif choice == '3':
            result = edit_api_keys()
            if result:
                key, value = result
                if save_settings_change(key, value):
                    console.print(f"[green]✅ {key} salvato con successo[/green]")
                    console.input("\nPremi invio per continuare...")
        elif choice == '4':
            edit_serpapi()
        elif choice == '5':
            result = edit_general_settings()
            if result:
                key, value = result
                if save_settings_change(key, value):
                    console.print(f"[green]✅ {key} impostato su: {value}[/green]")
                    console.input("\nPremi invio per continuare...")
        elif choice == '6':
            show_current_settings()
        else:
            console.print("[red]Opzione non valida[/red]")
            console.input("\nPremi invio per continuare...")

def main():
    settings = load_settings()
    
    lang = settings.get("lang", "it")
    topic = settings.get("topic")
    per_page = int(settings.get("articles_per_page", 15))
    provider = settings.get("provider", "ollama")
    serpapi_key = settings.get("serpapi_key")
    
    console = Console()
    

    
    try:
        ai_provider = create_ai_provider(provider, settings)
        model_name = get_model_name(ai_provider)
    except ValueError as e:
        console.print(f"[red]Errore configurazione AI: {e}[/red]")
        return
    
    verifier = None
    if serpapi_key and serpapi_key.strip():
        try:
            verifier = NewsVerifier(serpapi_key)
            console.print(f"[green]✅ SerpAPI configurata correttamente[/green]")
        except Exception as e:
            console.print(f"[red]❌ Errore inizializzazione SerpAPI: {e}[/red]")
            verifier = None
    else:
        console.print(f"[yellow]⚠️ SerpAPI non configurata - opzione verifica non disponibile[/yellow]")
        console.print(f"[dim]Per abilitare la verifica, aggiungi la tua serpapi_key in settings.ini[/dim]")
    

    
    console.print("\n[bold yellow]📰 Caricamento notizie...[/bold yellow]")
    
    if topic.startswith('http'):
        feed = topic
    else:
        feed = f"https://news.google.com/rss?hl={lang}&gl={lang.upper()}&ceid={topic or ''}"
    
    articles = fetch_articles(feed)
    if not articles:
        print("Nessun articolo trovato!")
        return
    
    current_page = 1
    total_pages = (len(articles) + per_page - 1) // per_page
    selected_idx = 0

    while True:
        show_table(articles, current_page, per_page, selected_idx, has_serpapi=bool(verifier))
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
            if selected_idx < len(articles) - 1:
                selected_idx += 1
            elif current_page < total_pages:
                current_page += 1
                selected_idx = 0
            else:
                console.print("[yellow]Sei già all'ultima notizia![/yellow]")
        elif user_input == 's':
            idx = selected_idx
            article = articles[idx]
            console.print(f"\n[bold yellow]📰 Scaricando e analizzando: {article['title']}[/bold yellow]")
            summary = summarize_article(article, ai_provider)
            console.print(Panel(summary, title=f"Sunto dell'articolo - {model_name}", border_style="cyan"))
            console.input("\nPremi invio per tornare alla lista")
        elif user_input == 'o':
            idx = selected_idx
            webbrowser.open(articles[idx]['link'])
            console.print(f"[bold green]Apro la notizia #{idx} nel browser...[/bold green]")
        elif user_input == 'a':
            idx = selected_idx
            article = articles[idx]
            show_article(article)
            console.print("\n[bold yellow]1. Riassunto (Agente 1)...[/bold yellow]")
            riassunto = agent_riassunto(article, ai_provider)
            console.print(Panel(riassunto, title=f"Riassunto - {model_name}", border_style="yellow"))
            console.print("\n[bold cyan]2. Implicazioni (Agente 2)...[/bold cyan]")
            implicazioni = agent_implicazioni(article, riassunto, ai_provider)
            console.print(Panel(implicazioni, title=f"Implicazioni - {model_name}", border_style="cyan"))
            console.print("\n[bold magenta]3. Teoria/Scenario (Agente 3)...[/bold magenta]")
            teoria = agent_teoria(article, riassunto, implicazioni, ai_provider)
            console.print(Panel(teoria, title=f"Teoria/Scenario - {model_name}", border_style="magenta"))
            console.input("\nPremi invio per tornare alla lista")
        elif user_input == 'v' and verifier:
            idx = selected_idx
            article = articles[idx]
            result = show_verification_menu()
            
            if result is None:
                continue
                
            verification_type, mode = result
            
            if verification_type == '1':
                console.print(f"\n[bold yellow]🔍 Verificando articolo: {article['title']} (modalità: {mode})[/bold yellow]")
                verification_data = verifier.verify_article(article, mode)
                agent_analysis = agent_verifica(article, verification_data, ai_provider)
                show_verification_results(verification_data, agent_analysis, model_name)
            elif verification_type == '2':
                console.print(f"\n[bold yellow]🔍 Validazione verità articolo: {article['title']} (modalità: {mode})[/bold yellow]")
                verification_data = verifier.verify_article(article, mode)
                agent_analysis = agent_validazione_verita(article, verification_data, ai_provider)
                show_verification_results(verification_data, agent_analysis, model_name)
            elif verification_type == '3':
                console.print(f"\n[bold magenta]🤖 Sistema multi-agente articolo: {article['title']} (modalità: {mode})...[/bold magenta]")
                verification_data = verifier.verify_article(article, mode)
                agent_analysis = run_multi_agent_verification(article, verification_data, ai_provider)
                show_verification_results(verification_data, agent_analysis, model_name)
            elif verification_type == '4':
                console.print(f"\n[bold green]🎯 Sistema multi-agente AUTOMATICO articolo: {article['title']} (modalità: {mode})...[/bold green]")
                verification_data = verifier.verify_article(article, mode)
                agent_analysis = run_multi_agent_verification(article, verification_data, ai_provider)
                show_verification_results(verification_data, agent_analysis, model_name)
            
            # Testo personalizzato
            elif verification_type == '5':
                custom_text = console.input("\nInserisci il testo da verificare: ")
                if custom_text.strip():
                    console.print(f"\n[bold yellow]🔍 Verificando testo personalizzato (modalità: {mode})...[/bold yellow]")
                    verification_data = verifier.verify_text(custom_text, mode)
                    agent_analysis = agent_verifica({'title': 'Testo personalizzato', 'summary': custom_text}, verification_data, ai_provider)
                    show_verification_results(verification_data, agent_analysis, model_name)
            elif verification_type == '5':
                custom_text = console.input("\nInserisci il testo da verificare: ")
                if custom_text.strip():
                    console.print(f"\n[bold yellow]🔍 Verificando testo personalizzato (modalità: {mode})...[/bold yellow]")
                    verification_data = verifier.verify_text(custom_text, mode)
                    agent_analysis = agent_verifica({'title': 'Testo personalizzato', 'summary': custom_text}, verification_data, ai_provider)
                    show_verification_results(verification_data, agent_analysis, model_name)
            elif verification_type == '6':
                custom_text = console.input("\nInserisci il testo da verificare: ")
                if custom_text.strip():
                    console.print(f"\n[bold blue]🧠 Verifica avanzata testo (step-by-step) (modalità: {mode})...[/bold blue]")
                    verification_data = verifier.verify_text(custom_text, mode)
                    agent_analysis = agent_verifica_advanced({'title': 'Testo personalizzato', 'summary': custom_text}, verification_data, ai_provider)
                    show_verification_results(verification_data, agent_analysis, model_name)
            elif verification_type == '7':
                custom_text = console.input("\nInserisci il testo da verificare: ")
                if custom_text.strip():
                    console.print(f"\n[bold blue]🧠 Validazione avanzata testo (modalità: {mode})...[/bold blue]")
                    verification_data = verifier.verify_text(custom_text, mode)
                    agent_analysis = agent_validazione_verita_advanced({'title': 'Testo personalizzato', 'summary': custom_text}, verification_data, ai_provider)
                    show_verification_results(verification_data, agent_analysis, model_name)
            elif verification_type == '8':
                custom_text = console.input("\nInserisci il testo da verificare: ")
                if custom_text.strip():
                    console.print(f"\n[bold green]🎯 Sistema multi-agente AUTOMATICO testo (modalità: {mode})...[/bold green]")
                    verification_data = verifier.verify_text(custom_text, mode)
                    agent_analysis = run_multi_agent_verification({'title': 'Testo personalizzato', 'summary': custom_text}, verification_data, ai_provider)
                    show_verification_results(verification_data, agent_analysis, model_name)
            
            console.input("\nPremi invio per tornare alla lista")
        elif user_input == 'c':
            handle_settings_menu(console)
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

if __name__ == "__main__":
    main()
