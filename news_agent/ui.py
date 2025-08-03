#!/usr/bin/env python

import os
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

def show_table(articles, page, per_page, selected_idx=None):
    os.system('clear' if os.name == 'posix' else 'cls')
    table = Table(title=f"Google News (Pagina {page})", border_style="green")
    table.add_column("#", justify="center", style="red", no_wrap=True)
    table.add_column("Data", style="yellow", no_wrap=True)
    table.add_column("Fonte", style="cyan", no_wrap=True)
    table.add_column("Titolo", style="white")
    start = (page - 1) * per_page
    end = start + per_page
    for i, article in enumerate(articles[start:end], start=start):
        style = "bold white on blue" if selected_idx == i else ("none" if i % 2 == 0 else "dim")
        table.add_row(str(i), article['date'][:16], article['author'], article['title'], style=style)
    console = Console()
    console.print(table)
    console.print("[i]Comandi: n=avanti, p=indietro, numero=apri dettagli, o=apri link browser, s=sunto globale, a=agenti LLM, q=esci[/i]")

def show_article(article):
    os.system('clear' if os.name == 'posix' else 'cls')
    article_panel = Panel(
        f"[bold]{article['title']}[/bold]\n\n"
        f"[dim]{article['date']}[/dim] [cyan]{article['author']}[/cyan]\n\n"
        f"{article['summary']}\n\n"
        f"[link={article['link']}]Leggi su Google News (premi 'o' per aprire)[/link]",
        title="Articolo dettagliato",
        border_style="white"
    )
    Console().print(article_panel)
