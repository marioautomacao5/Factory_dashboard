import plotly.graph_objects as go
import pandas as pd
import numpy as np


def linha_ritmo_global(ciclo_medio_global):
    ciclo_medio_global["hora"] = pd.to_datetime(ciclo_medio_global["hora"])
    agora = pd.Timestamp.now()
    limite = agora - pd.Timedelta(hours=2)
    df = ciclo_medio_global[ciclo_medio_global["hora"] >= limite]

    fig = go.Figure()

    for linha in df["LinhaProducao"].unique():
        sub = df[df["LinhaProducao"] == linha].copy()

        # 🔥 SIMULAÇÃO FAKE (ruído + leve oscilação)
        ruido = np.random.normal(0, 0.03, len(sub))
        tendencia = np.sin(np.linspace(0, 3, len(sub))) * 0.02
        sub["velocidade_fake"] = sub["velocidade_medida_global"] * (1 + ruido + tendencia)

        fig.add_trace(
            go.Scatter(
                x=sub["hora"],
                y=sub["velocidade_fake"],
                mode="lines+markers",
                name=linha,
                line=dict(shape="spline", smoothing=1.2)
            )
        )

    fig.update_layout(
        title={"text": "Real-Time Speed per Line", "font": {"color": "white"}},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        xaxis=dict(tickformat="%H:%M", gridcolor="#2d323e", showgrid=True),
        yaxis=dict(gridcolor="#2d323e", showgrid=True, autorange=True),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(font=dict(color="white"))
    )
    return fig


def linha_ritmo_soma(ciclo_medio_global):
    ciclo_medio_global["hora"] = pd.to_datetime(ciclo_medio_global["hora"])
    agora = pd.Timestamp.now()
    limite = agora - pd.Timedelta(hours=3)
    df = ciclo_medio_global[ciclo_medio_global["hora"] >= limite].copy()

    # 🔥 SIMULAÇÃO FAKE
    ruido = np.random.normal(0, 0.02, len(df))
    tendencia = np.sin(np.linspace(0, 3, len(df))) * 0.015
    df["velocidade_fake"] = df["velocidade_medida_global_soma"] * (1 + ruido + tendencia)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["hora"],
            y=df["velocidade_fake"],
            mode="lines+markers",
            name="Total Speed",
            line=dict(shape="spline", smoothing=1.2, color="#00CC96")
        )
    )

    fig.update_layout(
        title={"text": "Aggregated Real-Time Speed (Sum)", "font": {"color": "white"}},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        xaxis=dict(tickformat="%H:%M", gridcolor="#2d323e", showgrid=True),
        yaxis=dict(gridcolor="#2d323e", showgrid=True, autorange=True),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def linha_ritmo_media(ciclo_medio_global):
    ciclo_medio_global["hora"] = pd.to_datetime(ciclo_medio_global["hora"])
    agora = pd.Timestamp.now()
    limite = agora - pd.Timedelta(hours=3)
    df = ciclo_medio_global[ciclo_medio_global["hora"] >= limite].copy()

    # 🔥 SIMULAÇÃO FAKE
    ruido = np.random.normal(0, 0.02, len(df))
    tendencia = np.sin(np.linspace(0, 3, len(df))) * 0.015
    df["velocidade_fake"] = df["velocidade_medida_global_media"] * (1 + ruido + tendencia)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["hora"],
            y=df["velocidade_fake"],
            mode="lines+markers",
            name="Average Speed",
            line=dict(shape="spline", smoothing=1.2, color="#AB63FA")
        )
    )

    fig.update_layout(
        title={"text": "Aggregated Real-Time Speed (Average)", "font": {"color": "white"}},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        xaxis=dict(tickformat="%H:%M", gridcolor="#2d323e", showgrid=True),
        yaxis=dict(gridcolor="#2d323e", showgrid=True, autorange=True),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig