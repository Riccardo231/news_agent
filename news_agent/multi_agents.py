#!/usr/bin/env python

class MultiAgentVerificationSystem:
    """Sistema di verifica multi-agente specializzato"""
    
    def __init__(self, ai_provider):
        self.ai_provider = ai_provider
        self.results = {}
    
    def agent_router(self, article, verification_data):
        """🎯 Agente Router: Decide automaticamente il tipo di analisi"""
        print("🎯 Agente Router: Analizzando contenuto per scegliere metodo...")
        
        title = article.get('title', '')
        summary = article.get('summary', '')
        content = verification_data.get('full_content', '')
        
        prompt = f"""
        Sei l'Agente Router. Analizza il contenuto e scegli il metodo di verifica più appropriato.

        CONTENUTO DA ANALIZZARE:
        Titolo: {title}
        Riassunto: {summary}
        Contenuto: {content[:1000]}...

        TIPI DI ANALISI DISPONIBILI:
        1. SCIENTIFICA: Per studi, ricerche, scoperte, dati statistici
        2. NARRATIVA: Per eventi, cronaca, politica, economia
        3. TECNICA: Per tecnologia, innovazioni, prodotti
        4. MEDICA: Per salute, farmaci, terapie
        5. ECONOMICA: Per finanza, mercati, aziende
        6. POLITICA: Per elezioni, leggi, istituzioni
        7. CRONACA: Per eventi, incidenti, fatti di cronaca

        CRITERI DI SCELTA:
        - Presenza di studi scientifici → SCIENTIFICA
        - Dati statistici/percentuali → SCIENTIFICA
        - Eventi politici/elezioni → POLITICA
        - Notizie di cronaca → CRONACA
        - Tecnologia/innovazioni → TECNICA
        - Salute/medicina → MEDICA
        - Economia/finanza → ECONOMICA
        - Storie/racconti → NARRATIVA

        RISPOSTA FORMATO:
        TIPO: [SCIENTIFICA/NARRATIVA/TECNICA/MEDICA/ECONOMICA/POLITICA/CRONACA]
        MOTIVAZIONE: [spiega perché hai scelto questo tipo]
        APPROCCIO: [metodo specifico da usare]
        """
        
        try:
            result = self.ai_provider.generate(prompt, max_tokens=200)
            return result
        except Exception as e:
            print(f"⚠️ Errore Agente Router: {e}")
            return "TIPO: NARRATIVA\nMOTIVAZIONE: Fallback per errore\nAPPROCCIO: Analisi generale"
    
    def run_verification(self, article, verification_data):
        """Esegue la verifica completa usando tutti gli agenti"""
        print("🤖 Avvio sistema multi-agente di verifica...")
        
        # Prima determina il tipo di analisi
        try:
            self.results['router'] = self.agent_router(article, verification_data)
            print(f"🎯 Tipo di analisi scelto: {self.results['router']}")
        except Exception as e:
            print(f"⚠️ Errore Agente Router: {e}")
            self.results['router'] = "TIPO: NARRATIVA\nMOTIVAZIONE: Fallback\nAPPROCCIO: Analisi generale"
        
        try:
            try:
                self.results['investigator'] = self.agent_investigator(article, verification_data)
            except Exception as e:
                print(f"⚠️ Errore Agente Investigatore: {e}")
                self.results['investigator'] = "Errore nell'analisi delle fonti"
            
            try:
                self.results['methodologist'] = self.agent_methodologist(article, verification_data)
            except Exception as e:
                print(f"⚠️ Errore Agente Metodologo: {e}")
                self.results['methodologist'] = "Errore nella valutazione metodologica"
            
            try:
                self.results['fact_checker'] = self.agent_fact_checker(article, verification_data)
            except Exception as e:
                print(f"⚠️ Errore Agente Verificatore: {e}")
                self.results['fact_checker'] = "Errore nella verifica dei fatti"
            
            try:
                self.results['bias_analyzer'] = self.agent_bias_analyzer(article, verification_data)
            except Exception as e:
                print(f"⚠️ Errore Agente Giudice: {e}")
                self.results['bias_analyzer'] = "Errore nell'analisi dei bias"
            
            try:
                self.results['consensus_analyzer'] = self.agent_consensus_analyzer(article, verification_data)
            except Exception as e:
                print(f"⚠️ Errore Agente Consenso: {e}")
                self.results['consensus_analyzer'] = "Errore nell'analisi del consenso"
            
            try:
                self.results['synthesizer'] = self.agent_synthesizer(article, verification_data)
            except Exception as e:
                print(f"⚠️ Errore Agente Sintetizzatore: {e}")
                # Se il sintetizzatore fallisce, usa una sintesi semplificata
                self.results['synthesizer'] = self.create_simple_synthesis(article, verification_data)
            
            return self.results['synthesizer']
            
        except Exception as e:
            print(f"⚠️ Errore nel sistema multi-agente: {e}")
            print("🔄 Fallback a verifica standard...")
            
            from .agents import agent_verifica
            return agent_verifica(article, verification_data, self.ai_provider)
    
    def agent_investigator(self, article, verification_data):
        """🔍 Agente Investigatore: Cerca e raccoglie informazioni chiave"""
        print("🔍 Agente Investigatore: Analizzando fonti e informazioni...")
        
        fact_check_results = verification_data.get('fact_check_results', [])
        reliable_results = verification_data.get('reliable_sources_results', [])
        analysis_type = self.results.get('router', 'TIPO: NARRATIVA')
        
        sources_info = ""
        if fact_check_results and not fact_check_results[0].get('error'):
            for result in fact_check_results[:3]:
                title = result.get('title', '')
                source = result.get('source', '')
                search_query = result.get('search_query', '')
                sources_info += f"- {title} ({source}) - Query: {search_query}\n"
        
        reliable_info = ""
        if reliable_results and not reliable_results[0].get('error'):
            for result in reliable_results[:3]:
                title = result.get('title', '')
                source = result.get('source', '')
                search_query = result.get('search_query', '')
                reliable_info += f"- {title} ({source}) - Query: {search_query}\n"
        
        # Adatta l'analisi al tipo scelto
        type_specific_tasks = {
            'SCIENTIFICA': "1. Identifica studi scientifici e metodologie\n2. Controlla peer review e riviste\n3. Verifica dati statistici e campioni\n4. Cerca critiche metodologiche",
            'NARRATIVA': "1. Identifica eventi e cronologia\n2. Controlla testimonianze e fonti\n3. Verifica contesto storico\n4. Cerca contraddizioni narrative",
            'TECNICA': "1. Identifica specifiche tecniche\n2. Controlla brevetti e innovazioni\n3. Verifica claim tecnologici\n4. Cerca alternative esistenti",
            'MEDICA': "1. Identifica studi clinici\n2. Controlla approvazioni FDA/EMA\n3. Verifica effetti collaterali\n4. Cerca controversie mediche",
            'ECONOMICA': "1. Identifica dati economici\n2. Controlla fonti finanziarie\n3. Verifica trend di mercato\n4. Cerca analisi contrastanti",
            'POLITICA': "1. Identifica posizioni politiche\n2. Controlla dichiarazioni ufficiali\n3. Verifica contesto legislativo\n4. Cerca opposizioni e critiche",
            'CRONACA': "1. Identifica fatti di cronaca\n2. Controlla testimonianze\n3. Verifica timeline eventi\n4. Cerca versioni contrastanti"
        }
        
        default_tasks = type_specific_tasks.get('NARRATIVA', type_specific_tasks['NARRATIVA'])
        tasks = type_specific_tasks.get(analysis_type.split(':')[1].strip(), default_tasks)
        
        prompt = f"""
        Sei l'Agente Investigatore specializzato in analisi {analysis_type}.
        Analizza le fonti disponibili per identificare le informazioni chiave.

        NOTIZIA: {article.get('title', '')}
        TIPO ANALISI: {analysis_type}
        FONTI FACT-CHECKING: {sources_info}
        FONTI AFFIDABILI: {reliable_info}

        COMPITI SPECIALIZZATI:
        {tasks}

        RISULTATO:
        - Informazioni chiave trovate
        - Elementi specifici del tipo di analisi
        - Affermazioni da verificare
        - Fonti sospette o di parte
        """
        
        return self.ai_provider.generate(prompt, max_tokens=300)
    
    def agent_methodologist(self, article, verification_data):
        """📊 Agente Analista Metodologico: Valuta studi scientifici"""
        print("📊 Agente Analista Metodologico: Valutando metodologie...")
        
        investigator_result = self.results.get('investigator', '')
        
        prompt = f"""
        Sei l'Agente Analista Metodologico. Valuta la qualità degli studi scientifici identificati.

        NOTIZIA: {article.get('title', '')}
        STUDI IDENTIFICATI: {investigator_result}

        COMPITI:
        1. Per ogni studio scientifico menzionato:
           - Valuta la metodologia (campione, controlli, design)
           - Controlla la qualità della rivista (peer review, impact factor)
           - Verifica se esistono critiche metodologiche
           - Analizza la robustezza statistica

        2. Identifica:
           - Studi di alta qualità
           - Studi con metodologie deboli
           - Predatory journals
           - Gap metodologici

        RISULTATO:
        - Valutazione metodologica per studio
        - Qualità delle riviste
        - Critiche metodologiche trovate
        - Raccomandazioni
        """
        
        return self.ai_provider.generate(prompt, max_tokens=500)
    
    def agent_fact_checker(self, article, verification_data):
        """🎯 Agente Verificatore: Controlla fatti specifici"""
        print("🎯 Agente Verificatore: Verificando fatti specifici...")
        
        investigator_result = self.results.get('investigator', '')
        
        prompt = f"""
        Sei l'Agente Verificatore. Controlla la veridicità dei fatti specifici.

        NOTIZIA: {article.get('title', '')}
        AFFERMAZIONI IDENTIFICATE: {investigator_result}

        COMPITI:
        1. Per ogni affermazione specifica:
           - Verifica se è supportata da evidenze
           - Controlla se esistono contraddizioni
           - Valuta la qualità delle prove
           - Identifica gap informativi

        2. Cerca:
           - Contraddizioni tra fonti
           - Incoerenze temporali
           - Manipolazioni di dati
           - Affermazioni non verificabili

        RISULTATO:
        - Fatti verificati come corretti
        - Fatti contraddetti o dubbi
        - Contraddizioni trovate
        - Gap informativi identificati
        """
        
        return self.ai_provider.generate(prompt, max_tokens=400)
    
    def agent_bias_analyzer(self, article, verification_data):
        """⚖️ Agente Giudice: Analizza bias e conflitti di interesse"""
        print("⚖️ Agente Giudice: Analizzando bias e conflitti...")
        
        investigator_result = self.results.get('investigator', '')
        methodologist_result = self.results.get('methodologist', '')
        
        prompt = f"""
        Sei l'Agente Giudice. Analizza bias, conflitti di interesse e manipolazioni.

        NOTIZIA: {article.get('title', '')}
        FONTI IDENTIFICATE: {investigator_result}
        VALUTAZIONE METODOLOGICA: {methodologist_result}

        COMPITI:
        1. Analizza conflitti di interesse:
           - Chi ha finanziato gli studi?
           - Chi ha interesse a diffondere la notizia?
           - Ci sono legami economici/politici?

        2. Identifica bias:
           - Bias di selezione
           - Bias di conferma
           - Bias temporali
           - Bias geografici

        3. Cerca manipolazioni:
           - Cherry picking di dati
           - Manipolazione temporale
           - Contesti fuorvianti
           - Omissioni significative

        RISULTATO:
        - Conflitti di interesse identificati
        - Bias rilevati
        - Manipolazioni sospette
        - Livello di affidabilità delle fonti
        """
        
        return self.ai_provider.generate(prompt, max_tokens=500)
    
    def agent_consensus_analyzer(self, article, verification_data):
        """🌐 Agente Consenso: Analizza il consenso scientifico"""
        print("🌐 Agente Consenso: Analizzando consenso scientifico...")
        
        investigator_result = self.results.get('investigator', '')
        methodologist_result = self.results.get('methodologist', '')
        
        prompt = f"""
        Sei l'Agente Consenso. Analizza il consenso scientifico sul tema.

        NOTIZIA: {article.get('title', '')}
        STUDI IDENTIFICATI: {investigator_result}
        VALUTAZIONE METODOLOGICA: {methodologist_result}

        COMPITI:
        1. Valuta il consenso scientifico:
           - Quanti studi concordano?
           - Quanti contraddicono?
           - Qual è la distribuzione delle opinioni?
           - C'è un consenso forte o debole?

        2. Analizza la qualità del consenso:
           - Studi di alta qualità concordano?
           - Il consenso è basato su evidenze solide?
           - Ci sono controversie metodologiche?

        3. Identifica:
           - Consenso forte (90%+ concordano)
           - Consenso debole (60-90% concordano)
           - Controversia (nessun consenso chiaro)
           - Studi outlier e loro qualità

        RISULTATO:
        - Livello di consenso scientifico
        - Qualità del consenso
        - Controversie esistenti
        - Studi outlier e loro affidabilità
        """
        
        return self.ai_provider.generate(prompt, max_tokens=400)
    
    def agent_synthesizer(self, article, verification_data):
        """🧠 Agente Sintetizzatore: Combina tutti i risultati"""
        print("🧠 Agente Sintetizzatore: Sintetizzando risultati finali...")
        
        investigator = self.results.get('investigator', '')
        methodologist = self.results.get('methodologist', '')
        fact_checker = self.results.get('fact_checker', '')
        bias_analyzer = self.results.get('bias_analyzer', '')
        consensus_analyzer = self.results.get('consensus_analyzer', '')
        
        prompt = f"""
        Sei l'Agente Sintetizzatore. Combina tutti i risultati per il verdetto finale.

        NOTIZIA: {article.get('title', '')}
        
        RISULTATI DEGLI AGENTI:
        🔍 INVESTIGATORE: {investigator}
        📊 METODOLOGO: {methodologist}
        🎯 VERIFICATORE: {fact_checker}
        ⚖️ GIUDICE: {bias_analyzer}
        🌐 CONSENSO: {consensus_analyzer}

        COMPITI:
        1. Analizza tutti i risultati degli agenti
        2. Pesa le evidenze in base alla qualità
        3. Considera il consenso scientifico
        4. Valuta i conflitti di interesse
        5. Raggiungi un verdetto finale

        VERDETTO FINALE:
        1. **VERDETTO**: [VERA] / [FALSA] / [DUBBIA] / [INSUFFICIENTI DATI]
        2. **CONFIDENZA**: [ALTO 90%+] / [MEDIO 70-90%] / [BASSO <70%]
        3. **EVIDENZE CHIAVE**: Le prove più importanti
        4. **CONSENSO SCIENTIFICO**: Livello di accordo tra esperti
        5. **CONFLITTI DI INTERESSE**: Bias identificati
        6. **LIMITAZIONI**: Cosa non possiamo sapere
        7. **MOTIVAZIONE**: Spiega il ragionamento finale

        Rispondi in italiano con un'analisi strutturata e dettagliata.
        """
        
        return self.ai_provider.generate(prompt, max_tokens=500)
    
    def create_simple_synthesis(self, article, verification_data):
        """Crea una sintesi semplificata se il sintetizzatore fallisce"""
        print("📝 Creazione sintesi semplificata...")
        
        available_results = []
        for agent_name, result in self.results.items():
            if result and result != "Errore nell'analisi delle fonti" and not result.startswith("Errore"):
                available_results.append(f"{agent_name}: {result[:200]}...")
        
        synthesis = f"""
        🔍 VERIFICA MULTI-AGENTE - SINTESI SEMPLIFICATA
        
        📰 NOTIZIA: {article.get('title', '')}
        
        📊 RISULTATI DISPONIBILI:
        {chr(10).join(available_results) if available_results else "Nessun risultato disponibile"}
        
        ⚠️ NOTA: Alcuni agenti hanno fallito durante l'analisi.
        Si consiglia di riprovare o utilizzare la verifica standard.
        
        🎯 VERDETTO: [DUBBIA] - Analisi incompleta
        📊 CONFIDENZA: [BASSA] - Dati insufficienti
        """
        
        return synthesis

def run_multi_agent_verification(article, verification_data, ai_provider):
    """Funzione wrapper per eseguire la verifica multi-agente"""
    system = MultiAgentVerificationSystem(ai_provider)
    return system.run_verification(article, verification_data) 