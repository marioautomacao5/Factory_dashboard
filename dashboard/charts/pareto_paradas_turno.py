import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

def pareto_paradas_turno(df):
    if df.empty:
        return go.Figure()

    df = df.copy()

    # ======================================================
    # 🕒 FILTRO TURNO ATUAL
    # ======================================================
    hora = datetime.now().hour
    if 6 <= hora < 14:
        turno_atual = "1"
    elif 14 <= hora < 22:
        turno_atual = "2"
    else:
        turno_atual = "3"

    df = df[df["Turno"].str.contains(turno_atual, na=False)]

    if df.empty:
        return go.Figure()

    # ======================================================
    # ⏱️ GARANTIR FORMATO DE DURAÇÃO
    # ======================================================
    df["Duração"] = pd.to_timedelta(df["Duração"], errors="coerce")
    df["Duracao_min"] = df["Duração"].dt.total_seconds() / 60
    df = df.dropna(subset=["Duracao_min"])

    # ======================================================
    # 📊 AGRUPAR POR TEMPO TOTAL (TOP 5)
    # ======================================================
    df_group = (
        df.groupby("Motivo Parada")["Duracao_min"]
        .sum()
        .reset_index()
        .sort_values("Duracao_min", ascending=False)
        .head(5)
    )

    if df_group.empty:
        return go.Figure()

    # ======================================================
    # 📈 PARETO (% acumulado)
    # ======================================================
    total = df_group["Duracao_min"].sum()
    df_group["Perc"] = df_group["Duracao_min"] / total
    df_group["Perc_Acumulado"] = df_group["Perc"].cumsum()

    # ======================================================
    # 📊 CONSTRUÇÃO DO GRÁFICO
    # ======================================================
    fig = go.Figure()

    # Barras (Tempo Parado) - Cor vibrante para o Dark Mode
    fig.add_bar(
        x=df_group["Motivo Parada"],
        y=df_group["Duracao_min"],
        name="Tempo parado (min)",
        marker_color="#636EFA" 
    )

    # Linha acumulada (Eixo Secundário) - Cor de destaque (Laranja/Coral)
    fig.add_trace(
        go.Scatter(
            x=df_group["Motivo Parada"],
            y=df_group["Perc_Acumulado"],
            name="% Acumulado",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#EF553B", width=3),
            marker=dict(size=8)
        )
    )

    # ======================================================
    # 🎨 LAYOUT PARA STREAMLIT CLOUD (DARK)
    # ======================================================
    fig.update_layout(
        title={
            "text": "Pareto - Top 5 Paradas (Turno Atual)",
            "font": {"color": "white", "size": 18},
            "x": 0.5,
            "xanchor": "center"
        },
        
        # Transparência e Cores de Fonte
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",

        # Eixo Y Esquerdo (Minutos)
        yaxis=dict(
            title="Tempo parado (minutos)",
            gridcolor="#2d323e",
            zerolinecolor="#2d323e",
            tickfont=dict(color="white")
        ),

        # Eixo Y Direito (% Acumulada)
        yaxis2=dict(
            title="% Acumulado",
            overlaying="y",
            side="right",
            tickformat=".0%",
            gridcolor="rgba(0,0,0,0)", # Evita sobreposição de grades
            tickfont=dict(color="white"),
            range=[0, 1.1] # Dá um respiro no topo do gráfico
        ),

        xaxis=dict(
            title="Motivo Parada",
            gridcolor="#2d323e",
            tickfont=dict(color="white")
        ),

        # Legenda no topo centralizada
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        ),

        height=400,
        margin=dict(l=50, r=50, t=100, b=50)
    )

    return fig