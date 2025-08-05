#!/usr/bin/env python

import os
import webbrowser
import sys
import select
import tty
import termios
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

def get_arrow_input():
    """Gestisce l'input con supporto per le frecce su macOS/Linux"""
    console = Console()
    
    try:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(sys.stdin.fileno())
            
            ch = sys.stdin.read(1)

            if ch == '\x1b':

                ch2 = sys.stdin.read(1)
                if ch2 == '[':
                    ch3 = sys.stdin.read(1)
                    if ch3 == 'A':
                        return 'up'
                    elif ch3 == 'B':
                        return 'down'
                    elif ch3 == 'C':
                        return 'right'
                    elif ch3 == 'D':
                        return 'left'
            
            return ch.lower()
            
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    except (termios.error, OSError, AttributeError):
        return console.input().strip().lower()

def show_table(articles, page, per_page, selected_idx=None, has_serpapi=False):
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
    
    commands = "Comandi: ↑↓=naviga, Invio=apri articolo, n=avanti, p=indietro, numero=seleziona, o=apri link browser, s=sunto globale, a=agenti LLM, f=notizie successive"

    if has_serpapi:
        commands += ", v=verifica"
    
    commands += ", q=esci"
    console.print(f"[i]{commands}[/i]")

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

def show_verification_menu():
    """Mostra il menu delle opzioni di verifica"""
    console = Console()
    console.print("\n[bold cyan]🔍 MENU VERIFICA[/bold cyan]")
    console.print("1. Verifica articolo selezionato")
    console.print("2. Verifica testo personalizzato")
    console.print("0. Torna indietro")
    return console.input("\nSeleziona opzione (0-2): ").strip()

def show_verification_results(verification_data, agent_analysis=None):
    """Mostra i risultati della verifica"""
    os.system('clear' if os.name == 'posix' else 'cls')
    console = Console()
    
    console.print(Panel(
        verification_data.get('verification_summary', 'Nessun risultato'),
        title="📊 Risultati Verifica",
        border_style="cyan"
    ))
    
    if agent_analysis:
        console.print(Panel(
            agent_analysis,
            title="🤖 Analisi Agente LLM",
            border_style="yellow"
        ))
    
    fact_check_results = verification_data.get('fact_check_results', [])
    if fact_check_results and not fact_check_results[0].get('error'):
        console.print("\n[bold green]🔗 Link Fact-Checking:[/bold green]")
        for i, result in enumerate(fact_check_results[:3], 1):
            console.print(f"{i}. {result.get('title', '')}")
            console.print(f"   Link: {result.get('link', '')}")
    
    reliable_results = verification_data.get('reliable_sources_results', [])
    if reliable_results and not reliable_results[0].get('error'):
        console.print("\n[bold blue]📰 Fonti Affidabili:[/bold blue]")
        for i, result in enumerate(reliable_results[:3], 1):
            console.print(f"{i}. {result.get('title', '')} ({result.get('source', '')})")
            console.print(f"   Link: {result.get('link', '')}")
    
    console.input("\nPremi invio per tornare alla lista...")

def get_custom_text():
    """Chiede all'utente di inserire un testo personalizzato da verificare"""
    console = Console()
    console.print("\n[bold yellow]📝 Inserisci il testo da verificare:[/bold yellow]")
    console.print("(Scrivi il testo e premi invio, oppure premi invio senza testo per annullare)")
    
    text = console.input("Testo: ").strip()
    return text
