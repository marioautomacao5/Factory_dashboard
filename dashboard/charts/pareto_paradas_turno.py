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

    # converter para minutos (mais legível no gráfico)
    df["Duracao_min"] = df["Duração"].dt.total_seconds() / 60

    # remove nulos
    df = df.dropna(subset=["Duracao_min"])

    # ======================================================
    # 📊 AGRUPAR POR TEMPO TOTAL
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
    # 📊 GRÁFICO
    # ======================================================

    fig = go.Figure()

    # barras (tempo parado)
    fig.add_bar(
        x=df_group["Motivo Parada"],
        y=df_group["Duracao_min"],
        name="Tempo parado (min)"
    )

    # linha acumulada
    fig.add_trace(
        go.Scatter(
            x=df_group["Motivo Parada"],
            y=df_group["Perc_Acumulado"],
            name="% Acumulado",
            yaxis="y2",
            #mode="lines+markers"
        )
    )

    # layout
    fig.update_layout(
        title="Pareto - Top 5 Paradas por Tempo (Turno Atual)",

        yaxis=dict(title="Tempo parado (minutos)"),
        yaxis2=dict(
            title="% Acumulado",
            overlaying="y",
            side="right",
            tickformat=".0%"
        ),

        xaxis_title="Motivo Parada",

        # 🔥 legenda no topo REAL
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.15,
            xanchor="center",
            x=0.5
        ),

        # 🔥 ESSENCIAL
        margin=dict(t=100, b=100),

        # 🔥 ajuda no Streamlit
        height=400
    )

    return fig