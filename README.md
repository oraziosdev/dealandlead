# Click Academy – Lead & Vendite Dashboard

Una dashboard interattiva sviluppata con **Streamlit** che fornisce un'analisi completa dei lead e delle transazioni commerciali per Click Academy.

## 📊 Descrizione del Progetto

Questa applicazione consente di visualizzare e analizzare in tempo reale:

- **Lead totali** in ingresso
- - **Deal** (trattative commerciali) gestite
  - - **Vendite concluse** e relative statistiche
    - - **Tassi di conversione** per corso e provider
      - - **Analisi degli stati** dei lead e dei deal
        - - **Distribuzioni temporali** e tendenze
         
          - ## 🎯 Funzionalità Principali
         
          - - 📈 Panoramica generalizzata con KPI principali
            - - 📊 Grafici interattivi per l'analisi dei dati
              - - 🔍 Filtri avanzati per corso, provider e periodo
                - - 🔗 Unione e matching dei dati tra Lead e Deal
                  - - 💰 Analisi del fatturato e delle modalità di pagamento
                    - - 📋 Esplorazione dei dati grezzi con tabella dettagliata
                     
                      - ## 🚀 Come Usare
                     
                      - 1. Assicurati di avere Python 3.8+ installato
                        2. 2. Installa le dipendenze:
                           3.    ```bash
                                    pip install -r requirements.txt
                                    ```
                                 3. Esegui l'applicazione:
                                 4.    ```bash
                                          streamlit run app.py
                                          ```
                                       4. Apri il browser all'indirizzo `http://localhost:8501`
                                   
                                       5. ## 📁 Struttura del Progetto
                                   
                                       6. ```
                                          dealandlead/
                                          ├── app.py              # File principale dell'applicazione Streamlit
                                          ├── requirements.txt    # Dipendenze del progetto
                                          └── README.md          # Questo file
                                          ```

                                          ## 📊 Dati

                                          L'applicazione utilizza due dataset principali:
                                          - **Lead Archive**: Archivio completo dei lead ricevuti
                                          - - **Deal Data**: Dati delle trattative commerciali
                                           
                                            - I dati vengono uniti attraverso il campo `LEAD_ID` per fornire un'analisi integrata.
                                           
                                            - ## 🛠 Tecnologie Utilizzate
                                           
                                            - - **Streamlit**: Framework web interattivo per Python
                                              - - **Pandas**: Manipolazione e analisi dei dati
                                                - - **Plotly**: Visualizzazione interattiva dei grafici
                                                 
                                                  - ## 📝 Autor
                                                 
                                                  - Orazio Spoto - Click Academy Data Scientist
                                                 
                                                  - ## 📧 Contatti
                                                 
                                                  - Per domande o suggerimenti, puoi contattarmi a: orazio@oraziospoto.it
                                                 
                                                  - ---

                                                  **Ultimo aggiornamento:** Febbraio 2026
