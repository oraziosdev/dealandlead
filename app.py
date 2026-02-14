import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Config ──────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Click Academy – Lead & Vendite Dashboard",
    page_icon="📊",
    layout="wide",
)

# ── Helpers ─────────────────────────────────────────────────────────────────
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DEAL_FILE = os.path.join(DATA_DIR, "DealDatatable.xlsx")
LEAD_FILE = os.path.join(DATA_DIR, "LeadArchiveDatatable.xlsx")

COLORS = {
    "concluso": "#2ecc71",
    "promosso": "#3498db",
    "sospeso": "#f39c12",
    "non interessato": "#e74c3c",
    "non valido": "#95a5a6",
    "da richiamare": "#9b59b6",
    "respinto contabilità": "#e67e22",
}

LEAD_COLORS = {
    "non valido": "#95a5a6",
    "Chiuso": "#e74c3c",
    "in lavorazione": "#3498db",
    "libero": "#2ecc71",
    "non interessato": "#e67e22",
    "Non confermato": "#9b59b6",
}


@st.cache_data
def load_data():
    deals = pd.read_excel(DEAL_FILE)
    leads = pd.read_excel(LEAD_FILE)

    # Normalize column names
    deals.columns = deals.columns.str.strip()
    leads.columns = leads.columns.str.strip()

    # Parse dates
    for col in ["DATA INGRESSO LEAD", "DATA APPUNTAMENTI", "DATA ESITO"]:
        if col in deals.columns:
            deals[col] = pd.to_datetime(deals[col], errors="coerce")
    for col in ["DATA ENTRATA", "DATA USCITA"]:
        if col in leads.columns:
            leads[col] = pd.to_datetime(leads[col], errors="coerce")

    # Clean stato
    deals["STATO"] = deals["STATO"].astype(str).str.strip().str.lower()
    leads["STATO"] = leads["STATO"].astype(str).str.strip()

    # Flag vendite concluse
    deals["IS_CONCLUSO"] = deals["STATO"] == "concluso"

    return deals, leads


# ── Load data ───────────────────────────────────────────────────────────────
try:
    deals, leads = load_data()
except FileNotFoundError:
    st.error(
        "File non trovati. Assicurati che i file Excel siano nella cartella `data/`."
    )
    st.stop()

# ── Sidebar filters ────────────────────────────────────────────────────────
st.sidebar.image(
    "https://img.icons8.com/fluency/96/combo-chart.png", width=64
)
st.sidebar.title("Filtri")

# Corso filter
all_corsi = sorted(
    set(deals["CORSI"].dropna().unique()) | set(leads["CORSI"].dropna().unique())
)
sel_corsi = st.sidebar.multiselect("Corso", all_corsi, default=[])

# Provider filter (deal only)
all_providers = sorted(deals["PROVIDER"].dropna().unique())
sel_providers = st.sidebar.multiselect("Provider", all_providers, default=[])

# Date range
min_date = min(
    deals["DATA INGRESSO LEAD"].min(),
    leads["DATA ENTRATA"].min(),
)
max_date = max(
    deals["DATA INGRESSO LEAD"].max(),
    leads["DATA ENTRATA"].max(),
)
if pd.isna(min_date):
    min_date = pd.Timestamp("2025-01-01")
if pd.isna(max_date):
    max_date = pd.Timestamp.now()
date_range = st.sidebar.date_input(
    "Periodo",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date(),
)

# Apply filters
df_deals = deals.copy()
df_leads = leads.copy()

if sel_corsi:
    df_deals = df_deals[df_deals["CORSI"].isin(sel_corsi)]
    df_leads = df_leads[df_leads["CORSI"].isin(sel_corsi)]
if sel_providers:
    df_deals = df_deals[df_deals["PROVIDER"].isin(sel_providers)]
if len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    df_deals = df_deals[
        df_deals["DATA INGRESSO LEAD"].between(start, end, inclusive="both")
        | df_deals["DATA INGRESSO LEAD"].isna()
    ]
    df_leads = df_leads[
        df_leads["DATA ENTRATA"].between(start, end, inclusive="both")
        | df_leads["DATA ENTRATA"].isna()
    ]

conclusi = df_deals[df_deals["IS_CONCLUSO"]]
non_conclusi = df_deals[~df_deals["IS_CONCLUSO"]]

# ── Header ──────────────────────────────────────────────────────────────────
st.title("📊 Click Academy – Lead & Vendite")
st.markdown("Dashboard di confronto tra lead in ingresso e trattative commerciali.")

# ── KPI row ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Lead totali", f"{len(df_leads):,}")
k2.metric("Deal totali", f"{len(df_deals):,}")
k3.metric("Vendite concluse", f"{len(conclusi):,}")
tasso = (len(conclusi) / len(df_deals) * 100) if len(df_deals) > 0 else 0
k4.metric("Tasso conversione", f"{tasso:.1f}%")
fatturato = conclusi["IMPORTO CONTRATTO"].sum()
k5.metric("Fatturato concluso", f"€ {fatturato:,.0f}")

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# TAB LAYOUT
# ════════════════════════════════════════════════════════════════════════════
tab_overview, tab_deals, tab_leads, tab_match, tab_detail = st.tabs(
    [
        "📈 Overview",
        "💼 Deal / Vendite",
        "📋 Lead Archive",
        "🔗 Match Lead ↔ Deal",
        "🔍 Dettaglio dati",
    ]
)

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab_overview:
    st.subheader("Panoramica generale")

    col1, col2 = st.columns(2)

    # --- Deal per stato ---
    with col1:
        stato_counts = (
            df_deals["STATO"]
            .value_counts()
            .reset_index()
            .rename(columns={"STATO": "Stato", "count": "N"})
        )
        colors_mapped = [COLORS.get(s, "#bdc3c7") for s in stato_counts["Stato"]]
        fig = px.bar(
            stato_counts,
            x="Stato",
            y="N",
            color="Stato",
            color_discrete_map=COLORS,
            title="Deal per Stato",
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # --- Lead per stato ---
    with col2:
        lead_stato = (
            df_leads["STATO"]
            .value_counts()
            .reset_index()
            .rename(columns={"STATO": "Stato", "count": "N"})
        )
        fig2 = px.bar(
            lead_stato,
            x="Stato",
            y="N",
            color="Stato",
            color_discrete_map=LEAD_COLORS,
            title="Lead per Stato",
        )
        fig2.update_layout(showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    # --- Confronto Lead vs Conclusi per Corso ---
    st.subheader("Lead vs Vendite Concluse per Corso")

    lead_per_corso = (
        df_leads.groupby("CORSI").size().reset_index(name="Lead")
    )
    deal_conclusi_per_corso = (
        conclusi.groupby("CORSI").size().reset_index(name="Conclusi")
    )
    confronto = lead_per_corso.merge(deal_conclusi_per_corso, on="CORSI", how="outer").fillna(0)
    confronto["Conclusi"] = confronto["Conclusi"].astype(int)
    confronto["Lead"] = confronto["Lead"].astype(int)
    confronto = confronto.sort_values("Lead", ascending=True)

    fig3 = go.Figure()
    fig3.add_trace(
        go.Bar(
            y=confronto["CORSI"],
            x=confronto["Lead"],
            name="Lead",
            orientation="h",
            marker_color="#3498db",
        )
    )
    fig3.add_trace(
        go.Bar(
            y=confronto["CORSI"],
            x=confronto["Conclusi"],
            name="Vendite Concluse",
            orientation="h",
            marker_color="#2ecc71",
        )
    )
    fig3.update_layout(
        barmode="group",
        height=500,
        title="Confronto Lead ricevuti vs Vendite concluse per Corso",
        xaxis_title="Conteggio",
        yaxis_title="",
    )
    st.plotly_chart(fig3, use_container_width=True)

    # --- Tasso conversione per corso ---
    st.subheader("Tasso di conversione per Corso")
    deal_per_corso_all = df_deals.groupby("CORSI").size().reset_index(name="Deal Totali")
    conv = deal_per_corso_all.merge(deal_conclusi_per_corso, on="CORSI", how="left").fillna(0)
    conv["Conclusi"] = conv["Conclusi"].astype(int)
    conv["Tasso %"] = (conv["Conclusi"] / conv["Deal Totali"] * 100).round(1)
    conv = conv.sort_values("Tasso %", ascending=True)

    fig_conv = px.bar(
        conv,
        y="CORSI",
        x="Tasso %",
        orientation="h",
        color="Tasso %",
        color_continuous_scale=["#e74c3c", "#f39c12", "#2ecc71"],
        title="Tasso di conversione Deal → Concluso per Corso",
    )
    fig_conv.update_layout(height=450)
    st.plotly_chart(fig_conv, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – DEAL / VENDITE
# ════════════════════════════════════════════════════════════════════════════
with tab_deals:
    st.subheader("Vendite Concluse")

    c1, c2 = st.columns(2)
    with c1:
        # Conclusi per corso
        conc_corso = conclusi.groupby("CORSI").size().reset_index(name="N")
        fig_cc = px.pie(
            conc_corso,
            names="CORSI",
            values="N",
            title="Vendite concluse per Corso",
            hole=0.4,
        )
        st.plotly_chart(fig_cc, use_container_width=True)

    with c2:
        # Conclusi per provider
        conc_prov = conclusi.groupby("PROVIDER").size().reset_index(name="N")
        fig_cp = px.pie(
            conc_prov,
            names="PROVIDER",
            values="N",
            title="Vendite concluse per Provider",
            hole=0.4,
        )
        st.plotly_chart(fig_cp, use_container_width=True)

    # Fatturato per corso
    fatt_corso = (
        conclusi.groupby("CORSI")["IMPORTO CONTRATTO"]
        .sum()
        .reset_index()
        .sort_values("IMPORTO CONTRATTO", ascending=True)
    )
    fig_fatt = px.bar(
        fatt_corso,
        y="CORSI",
        x="IMPORTO CONTRATTO",
        orientation="h",
        title="Fatturato per Corso (vendite concluse)",
        color="IMPORTO CONTRATTO",
        color_continuous_scale="Greens",
    )
    fig_fatt.update_layout(height=400)
    st.plotly_chart(fig_fatt, use_container_width=True)

    # Modalità di pagamento
    c3, c4 = st.columns(2)
    with c3:
        pag = conclusi.groupby("MODALITÀ PAGAMENTO").size().reset_index(name="N")
        fig_pag = px.pie(pag, names="MODALITÀ PAGAMENTO", values="N",
                         title="Modalità di pagamento (conclusi)", hole=0.4)
        st.plotly_chart(fig_pag, use_container_width=True)

    with c4:
        # Commerciale performance
        comm = conclusi.groupby("COMMERCIALE").size().reset_index(name="N").sort_values("N", ascending=True)
        fig_comm = px.bar(comm, y="COMMERCIALE", x="N", orientation="h",
                          title="Vendite concluse per Commerciale", color="N",
                          color_continuous_scale="Blues")
        st.plotly_chart(fig_comm, use_container_width=True)

    st.divider()
    st.subheader("Deal NON conclusi (altri stati)")

    c5, c6 = st.columns(2)
    with c5:
        nc_stato = non_conclusi["STATO"].value_counts().reset_index()
        nc_stato.columns = ["Stato", "N"]
        fig_nc = px.pie(nc_stato, names="Stato", values="N",
                        title="Distribuzione stati non conclusi",
                        color="Stato", color_discrete_map=COLORS, hole=0.4)
        st.plotly_chart(fig_nc, use_container_width=True)

    with c6:
        # Sottostato dei non conclusi
        nc_sotto = (
            non_conclusi["SOTTOSTATO"]
            .dropna()
            .value_counts()
            .head(15)
            .reset_index()
        )
        nc_sotto.columns = ["Sottostato", "N"]
        fig_sotto = px.bar(nc_sotto, x="N", y="Sottostato", orientation="h",
                           title="Top 15 Sotto-stati (deal non conclusi)",
                           color="N", color_continuous_scale="Reds")
        fig_sotto.update_layout(height=450)
        st.plotly_chart(fig_sotto, use_container_width=True)

    # Non conclusi per corso
    nc_corso = non_conclusi.groupby(["CORSI", "STATO"]).size().reset_index(name="N")
    fig_nc_corso = px.bar(
        nc_corso,
        x="CORSI",
        y="N",
        color="STATO",
        color_discrete_map=COLORS,
        title="Deal non conclusi per Corso e Stato",
        barmode="stack",
    )
    fig_nc_corso.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_nc_corso, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 – LEAD ARCHIVE
# ════════════════════════════════════════════════════════════════════════════
with tab_leads:
    st.subheader("Analisi Lead Archive")

    c1, c2 = st.columns(2)

    with c1:
        # Lead per stato
        ls = df_leads["STATO"].value_counts().reset_index()
        ls.columns = ["Stato", "N"]
        fig_ls = px.pie(ls, names="Stato", values="N",
                        title="Lead per Stato",
                        color="Stato", color_discrete_map=LEAD_COLORS, hole=0.4)
        st.plotly_chart(fig_ls, use_container_width=True)

    with c2:
        # Lead per provider
        lp = df_leads["PROVIDER"].value_counts().reset_index()
        lp.columns = ["Provider", "N"]
        fig_lp = px.pie(lp, names="Provider", values="N",
                        title="Lead per Provider", hole=0.4)
        st.plotly_chart(fig_lp, use_container_width=True)

    # Lead per corso
    st.subheader("Lead per Corso")
    lc = df_leads.groupby("CORSI").size().reset_index(name="N").sort_values("N", ascending=True)
    fig_lc = px.bar(lc, y="CORSI", x="N", orientation="h",
                    title="Numero di Lead per Corso", color="N",
                    color_continuous_scale="Blues")
    fig_lc.update_layout(height=500)
    st.plotly_chart(fig_lc, use_container_width=True)

    # Lead per corso e stato (stacked)
    st.subheader("Lead per Corso e Stato")
    lcs = df_leads.groupby(["CORSI", "STATO"]).size().reset_index(name="N")
    fig_lcs = px.bar(lcs, x="CORSI", y="N", color="STATO",
                     color_discrete_map=LEAD_COLORS,
                     title="Distribuzione stati Lead per Corso",
                     barmode="stack")
    fig_lcs.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig_lcs, use_container_width=True)

    # Sotto-stato lead
    st.subheader("Sotto-stati Lead")
    lss = df_leads["SOTTOSTATO"].dropna().value_counts().head(20).reset_index()
    lss.columns = ["Sottostato", "N"]
    fig_lss = px.bar(lss, x="N", y="Sottostato", orientation="h",
                     title="Top 20 Sotto-stati Lead", color="N",
                     color_continuous_scale="Oranges")
    fig_lss.update_layout(height=500)
    st.plotly_chart(fig_lss, use_container_width=True)

    # Costo lead per provider
    st.subheader("Costo Lead per Provider")
    cost = df_leads.groupby("PROVIDER").agg(
        Costo_Totale=("COSTO LEAD", "sum"),
        N_Lead=("COSTO LEAD", "count"),
        Costo_Medio=("COSTO LEAD", "mean"),
    ).reset_index().sort_values("Costo_Totale", ascending=True)

    fig_cost = px.bar(cost, y="PROVIDER", x="Costo_Totale", orientation="h",
                      title="Costo totale Lead per Provider",
                      color="Costo_Medio",
                      color_continuous_scale="YlOrRd",
                      hover_data=["N_Lead", "Costo_Medio"])
    st.plotly_chart(fig_cost, use_container_width=True)

    # Timeline lead entrata
    st.subheader("Andamento Lead nel tempo")
    leads_time = df_leads.dropna(subset=["DATA ENTRATA"]).copy()
    leads_time["Settimana"] = leads_time["DATA ENTRATA"].dt.to_period("W").dt.start_time
    lt = leads_time.groupby("Settimana").size().reset_index(name="N")
    fig_lt = px.line(lt, x="Settimana", y="N", title="Lead in ingresso per settimana",
                     markers=True)
    st.plotly_chart(fig_lt, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 – MATCH LEAD ↔ DEAL
# ════════════════════════════════════════════════════════════════════════════
with tab_match:
    st.subheader("Unione Lead ↔ Deal tramite LEAD_ID (colonna B)")
    st.markdown(
        "Questa sezione unisce i dati dei due file utilizzando **LEAD_ID** "
        "(colonna B di entrambi i file) come chiave di collegamento."
    )

    # Merge
    merged = df_leads.merge(
        df_deals,
        left_on="ID LEAD",
        right_on="LEAD_ID",
        how="outer",
        suffixes=("_lead", "_deal"),
        indicator=True,
    )

    # Stats
    both = merged[merged["_merge"] == "both"]
    only_lead = merged[merged["_merge"] == "left_only"]
    only_deal = merged[merged["_merge"] == "right_only"]

    m1, m2, m3 = st.columns(3)
    m1.metric("Match (entrambi)", f"{len(both):,}")
    m2.metric("Solo in Lead Archive", f"{len(only_lead):,}")
    m3.metric("Solo in Deal", f"{len(only_deal):,}")

    # Venn-like chart
    fig_venn = go.Figure()
    fig_venn.add_trace(go.Bar(
        x=["Solo Lead Archive", "Match", "Solo Deal"],
        y=[len(only_lead), len(both), len(only_deal)],
        marker_color=["#3498db", "#2ecc71", "#e74c3c"],
        text=[len(only_lead), len(both), len(only_deal)],
        textposition="auto",
    ))
    fig_venn.update_layout(title="Distribuzione Match Lead ↔ Deal")
    st.plotly_chart(fig_venn, use_container_width=True)

    # Matched records: lead stato vs deal stato
    if len(both) > 0:
        st.subheader("Stato Lead vs Stato Deal (record matchati)")

        c1, c2 = st.columns(2)
        with c1:
            stato_lead_m = both["STATO_lead"].value_counts().reset_index()
            stato_lead_m.columns = ["Stato Lead", "N"]
            fig_slm = px.pie(stato_lead_m, names="Stato Lead", values="N",
                             title="Stato Lead (matchati)", hole=0.4)
            st.plotly_chart(fig_slm, use_container_width=True)

        with c2:
            stato_deal_m = both["STATO_deal"].value_counts().reset_index()
            stato_deal_m.columns = ["Stato Deal", "N"]
            fig_sdm = px.pie(stato_deal_m, names="Stato Deal", values="N",
                             title="Stato Deal (matchati)", hole=0.4,
                             color="Stato Deal", color_discrete_map=COLORS)
            st.plotly_chart(fig_sdm, use_container_width=True)

        # Heatmap Lead Stato → Deal Stato
        st.subheader("Matrice Stato Lead → Stato Deal")
        cross = pd.crosstab(both["STATO_lead"], both["STATO_deal"])
        fig_heat = px.imshow(
            cross,
            text_auto=True,
            color_continuous_scale="YlGnBu",
            title="Heatmap: come i Lead si distribuiscono nei diversi stati Deal",
            labels=dict(x="Stato Deal", y="Stato Lead", color="Conteggio"),
        )
        fig_heat.update_layout(height=400)
        st.plotly_chart(fig_heat, use_container_width=True)

        # Funnel: lead → deal → concluso
        st.subheader("Funnel: Lead → Deal → Vendita Conclusa")
        n_leads_tot = len(df_leads)
        n_matched = len(both)
        n_conclusi_match = len(both[both["STATO_deal"] == "concluso"])

        fig_funnel = go.Figure(go.Funnel(
            y=["Lead Totali", "Lead con Deal", "Vendite Concluse"],
            x=[n_leads_tot, n_matched, n_conclusi_match],
            textinfo="value+percent initial",
            marker_color=["#3498db", "#f39c12", "#2ecc71"],
        ))
        fig_funnel.update_layout(title="Funnel di conversione")
        st.plotly_chart(fig_funnel, use_container_width=True)

        # Tempo medio dal lead alla vendita
        if "DATA ENTRATA" in both.columns and "DATA ESITO" in both.columns:
            both_conclusi = both[both["STATO_deal"] == "concluso"].copy()
            if len(both_conclusi) > 0:
                both_conclusi["Giorni"] = (
                    both_conclusi["DATA ESITO"] - both_conclusi["DATA ENTRATA"]
                ).dt.days
                valid = both_conclusi.dropna(subset=["Giorni"])
                if len(valid) > 0:
                    avg_days = valid["Giorni"].mean()
                    st.metric("Tempo medio Lead → Conclusione", f"{avg_days:.0f} giorni")

    # Tabella matchata
    st.subheader("Tabella dati uniti")
    show_cols = [
        "ID LEAD", "COGNOME_lead", "NOME_lead", "CORSI_lead",
        "STATO_lead", "PROVIDER_lead", "STATO_deal", "CORSI_deal",
        "IMPORTO CONTRATTO", "COMMERCIALE", "_merge",
    ]
    available_cols = [c for c in show_cols if c in merged.columns]
    st.dataframe(
        merged[available_cols].rename(columns={"_merge": "Presenza"}),
        use_container_width=True,
        height=400,
    )


# ════════════════════════════════════════════════════════════════════════════
# TAB 5 – DETTAGLIO DATI
# ════════════════════════════════════════════════════════════════════════════
with tab_detail:
    st.subheader("Esplora i dati grezzi")

    data_choice = st.radio(
        "Dataset", ["Deal (DealDatatable)", "Lead (LeadArchiveDatatable)", "Dati uniti"],
        horizontal=True,
    )

    if data_choice == "Deal (DealDatatable)":
        search = st.text_input("Cerca (cognome, email, corso...)", key="search_deal")
        display = df_deals.copy()
        if search:
            mask = display.apply(
                lambda row: row.astype(str).str.contains(search, case=False).any(),
                axis=1,
            )
            display = display[mask]
        st.dataframe(display, use_container_width=True, height=500)
        st.download_button(
            "Scarica CSV Deal filtrati",
            display.to_csv(index=False).encode("utf-8"),
            "deal_filtrati.csv",
        )

    elif data_choice == "Lead (LeadArchiveDatatable)":
        search = st.text_input("Cerca (cognome, email, corso...)", key="search_lead")
        display = df_leads.copy()
        if search:
            mask = display.apply(
                lambda row: row.astype(str).str.contains(search, case=False).any(),
                axis=1,
            )
            display = display[mask]
        st.dataframe(display, use_container_width=True, height=500)
        st.download_button(
            "Scarica CSV Lead filtrati",
            display.to_csv(index=False).encode("utf-8"),
            "lead_filtrati.csv",
        )

    else:
        search = st.text_input("Cerca", key="search_merged")
        display = merged.copy()
        if search:
            mask = display.apply(
                lambda row: row.astype(str).str.contains(search, case=False).any(),
                axis=1,
            )
            display = display[mask]
        st.dataframe(display, use_container_width=True, height=500)
        st.download_button(
            "Scarica CSV dati uniti",
            display.to_csv(index=False).encode("utf-8"),
            "dati_uniti.csv",
        )
