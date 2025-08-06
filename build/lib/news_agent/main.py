#!/usr/bin/env python

from .settings import load_settings
from .fetcher import fetch_articles
from .agents import agent_riassunto, agent_implicazioni, agent_teoria, summarize_article, agent_verifica, agent_validazione_verita
from .ui import show_table, show_article, get_arrow_input, show_verification_menu, show_verification_results
from .ai_providers import create_ai_provider
from .verifier import NewsVerifier
from rich.panel import Panel
from rich.console import Console
import requests
import webbrowser
import sys

def get_model_name(ai_provider):
    """Ottiene il nome del modello dall'AI provider"""
    if hasattr(ai_provider, 'model'):
        return ai_provider.model
    return "Modello sconosciuto"

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
    if serpapi_key:
        verifier = NewsVerifier(serpapi_key)
    
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
            verification_type = show_verification_menu()
            
            if verification_type == '1':
                console.print(f"\n[bold yellow]🔍 Verificando articolo: {article['title']}[/bold yellow]")
                verification_data = verifier.verify_article(article)
                agent_analysis = agent_verifica(article, verification_data, ai_provider)
                show_verification_results(verification_data, agent_analysis, model_name)
            elif verification_type == '2':
                custom_text = console.input("\nInserisci il testo da verificare: ")
                if custom_text.strip():
                    console.print(f"\n[bold yellow]🔍 Verificando testo personalizzato...[/bold yellow]")
                    verification_data = verifier.verify_text(custom_text)
                    agent_analysis = agent_verifica({'title': 'Testo personalizzato', 'summary': custom_text}, verification_data, ai_provider)
                    show_verification_results(verification_data, agent_analysis, model_name)
            elif verification_type == '3':
                console.print(f"\n[bold yellow]🔍 Verificando validazione della verità di: {article['title']}[/bold yellow]")
                verification_data = verifier.verify_article(article)
                agent_analysis = agent_validazione_verita(article, verification_data, ai_provider)
                show_verification_results(verification_data, agent_analysis, model_name)
            
            console.input("\nPremi invio per tornare alla lista")
        elif user_input == 'c':
            console.print("[bold yellow]🔍 Cerco i modelli disponibili su Ollama...[/bold yellow]")
            try:
                ollama_url = settings.get("ollama_url", "http://localhost:11434/generate")
                resp = requests.get(ollama_url.replace("/generate", "/tags"))
                resp.raise_for_status()
                models_data = resp.json().get("models", [])

                if not models_data:
                    console.print("[red]❌ Nessun modello trovato su Ollama.[/red]")
                    return

                # Ordina i modelli per dimensione (campo 'size'), decrescente
                models_sorted = sorted(models_data, key=lambda m: m.get("size", 0), reverse=True)

                if len(models_sorted) < 3:
                    console.print("[red]⚠️ Trovati meno di 3 modelli, scegli manualmente.[/red]")
                    for i, m in enumerate(models_sorted):
                        console.print(f"{i+1}: {m['name']}")
                    idx = int(console.input("Inserisci il numero del modello da usare: ").strip()) - 1
                    if 0 <= idx < len(models_sorted):
                        model = models_sorted[idx]["name"]
                else:
                    model_light = models_sorted[-1]["name"]
                    model_medium = models_sorted[len(models_sorted) // 2]["name"]
                    model_heavy = models_sorted[0]["name"]

                    console.print("\n[bold yellow]Scegli un modello:[/bold yellow]")
                    console.print(f"1: modello più leggero → [green]{model_light}[/green]")
                    console.print(f"2: modello intermedio → [cyan]{model_medium}[/cyan]")
                    console.print(f"3: modello più pesante → [magenta]{model_heavy}[/magenta]")
                    console.print("p: personalizzato")

                    new_model = console.input("Scelta: ").strip()
                    if new_model == '1':
                        model = model_light
                    elif new_model == '2':
                        model = model_medium
                    elif new_model == '3':
                        model = model_heavy
                    elif new_model == 'p':
                        model = console.input("Inserisci il nome del modello personalizzato: ").strip()

                # 🔄 aggiorna il setting e salva nel file ini
                settings["model"] = model
                from .settings import save_settings
                save_settings(settings)

                console.print(f"[bold green]✅ Modello aggiornato a: {model} e salvato in settings.ini[/bold green]")

            except Exception as e:
                console.print(f"[red]❌ Errore nel recupero dei modelli: {e}[/red]")
        elif user_input == 'l':
            console.print("\n[bold yellow]🌍 Cambia lingua delle notizie[/bold yellow]")

            lingue = {
                "1": ("it", "🇮🇹 Italiano"),
                "2": ("en", "🇬🇧 English"),
                "3": ("de", "🇩🇪 Deutsch"),
                "4": ("fr", "🇫🇷 Français"),
                "5": ("es", "🇪🇸 Español"),
                "6": ("pt", "🇵🇹 Português"),
                "7": ("nl", "🇳🇱 Nederlands"),
                "8": ("pl", "🇵🇱 Polski"),
                "9": ("tr", "🇹🇷 Türkçe"),
                "p": ("manual", "✍️ Inserisci codice manuale")
            }

            for k, (code, name) in lingue.items():
                console.print(f"{k}: {name} [{code}]")

            scelta = console.input("\nScegli una lingua (1-9, p): ").strip()

            if scelta in lingue:
                if scelta == 'p':
                    new_lang = console.input("Inserisci codice lingua (es. it, en, de): ").strip().lower()
                else:
                    new_lang = lingue[scelta][0]

                if len(new_lang) >= 1:
                    settings["lang"] = new_lang
                    from .settings import save_settings
                    save_settings(settings)
                    console.print(f"[bold green]✅ Lingua aggiornata a: {new_lang} e salvata in settings.ini[/bold green]")

                    feed = f"https://news.google.com/rss?hl={new_lang}&gl={new_lang.upper()}&ceid={topic or ''}"
                    articles = fetch_articles(feed)
                    if not articles:
                        print("Nessun articolo trovato!")
                        return
                else:
                    console.print("[red]❌ Codice lingua non valido (usa due lettere tipo 'it', 'en')[/red]")
            else:
                console.print("[red]❌ Scelta non valida.[/red]")
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
