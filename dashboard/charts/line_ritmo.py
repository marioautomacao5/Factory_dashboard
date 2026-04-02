import plotly.graph_objects as go
import pandas as pd

def linha_ritmo_global(ciclo_medio_global):
    ciclo_medio_global["hora"] = pd.to_datetime(ciclo_medio_global["hora"])
    agora = ciclo_medio_global["hora"].max()
    limite = agora - pd.Timedelta(hours=2)
    df = ciclo_medio_global[ciclo_medio_global["hora"] >= limite]

    fig = go.Figure()

    for linha in df["LinhaProducao"].unique():
        sub = df[df["LinhaProducao"] == linha]
        fig.add_trace(
            go.Scatter(
                x=sub["hora"],
                y=sub["velocidade_medida_global"],
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
    agora = ciclo_medio_global["hora"].max()
    limite = agora - pd.Timedelta(hours=3)
    df = ciclo_medio_global[ciclo_medio_global["hora"] >= limite]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["hora"],
            y=df["velocidade_medida_global_soma"],
            mode="lines+markers",
            name="Velocidade Total",
            line=dict(shape="spline", smoothing=1.2, color="#00CC96") # Cor diferente para destaque
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
    agora = ciclo_medio_global["hora"].max()
    limite = agora - pd.Timedelta(hours=3)
    df = ciclo_medio_global[ciclo_medio_global["hora"] >= limite]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["hora"],
            y=df["velocidade_medida_global_media"],
            mode="lines+markers",
            name="Velocidade Média",
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