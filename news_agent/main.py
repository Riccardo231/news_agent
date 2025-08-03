#!/usr/bin/env python

from .settings import load_settings
from .fetcher import fetch_articles
from .agents import agent_riassunto, agent_implicazioni, agent_teoria, summarize_with_ollama
from .ui import show_table, show_article
from rich.panel import Panel
from rich.console import Console
import webbrowser

def main():
    settings = load_settings()
    lang = settings.get("lang", "it")
    topic = settings.get("topic")
    per_page = int(settings.get("articles_per_page", 15))
    model = settings.get("model", "qwen2:7b-instruct")
    ollama_url = settings.get("ollama_url", "http://localhost:11434/api/generate")
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
        show_table(articles, current_page, per_page, selected_idx)
        user_input = console.input("Seleziona (n/p/numero/o/a/s/q): ").strip().lower()

        if user_input == 'q':
            break
        elif user_input == 'n' and current_page < total_pages:
            current_page += 1
        elif user_input == 'p' and current_page > 1:
            current_page -= 1
        elif user_input == 's':
            summary = summarize_with_ollama(articles, model, ollama_url)
            console.print(Panel(summary, title="Sunto globale delle notizie", border_style="cyan"))
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
            riassunto = agent_riassunto(article, model, ollama_url)
            console.print(Panel(riassunto, title="Riassunto", border_style="yellow"))
            console.print("\n[bold cyan]2. Implicazioni (Agente 2)...[/bold cyan]")
            implicazioni = agent_implicazioni(article, riassunto, model, ollama_url)
            console.print(Panel(implicazioni, title="Implicazioni", border_style="cyan"))
            console.print("\n[bold magenta]3. Teoria/Scenario (Agente 3)...[/bold magenta]")
            teoria = agent_teoria(article, riassunto, implicazioni, model, ollama_url)
            console.print(Panel(teoria, title="Teoria/Scenario", border_style="magenta"))
            console.input("\nPremi invio per tornare alla lista")
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
