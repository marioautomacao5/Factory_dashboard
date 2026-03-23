import plotly.graph_objects as go
import pandas as pd

def linha_ritmo_global(ciclo_medio_global):

    # ✅ Garantir datetime
    ciclo_medio_global["hora"] = pd.to_datetime(ciclo_medio_global["hora"])

    # ✅ Filtro últimas 3 horas
    agora = pd.Timestamp.now()
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
        title="Velocidade instantânea por linha",
        yaxis=dict(autorange=True),
        xaxis_title="Hora",
        yaxis_title="Velocidade medida [Emb/h]",
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(tickformat="%H:%M", showgrid=False)
    )

    return fig

def linha_ritmo_soma(ciclo_medio_global):

    ciclo_medio_global["hora"] = pd.to_datetime(ciclo_medio_global["hora"])

    agora = pd.Timestamp.now()
    limite = agora - pd.Timedelta(hours=3)

    df = ciclo_medio_global[ciclo_medio_global["hora"] >= limite]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["hora"],
            y=df["velocidade_medida_global_soma"],
            mode="lines+markers",
            name="Velocidade Total",
            line=dict(shape="spline", smoothing=1.2)
        )
    )

    fig.update_layout(
        title="Velocidade instantânea agregada por soma",
        yaxis=dict(autorange=True),
        xaxis_title="Hora",
        yaxis_title="Velocidade medida [Emb/h]",
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(tickformat="%H:%M", showgrid=False)
    )

    return fig

def linha_ritmo_media(ciclo_medio_global):

    ciclo_medio_global["hora"] = pd.to_datetime(ciclo_medio_global["hora"])

    agora = pd.Timestamp.now()
    limite = agora - pd.Timedelta(hours=3)

    df = ciclo_medio_global[ciclo_medio_global["hora"] >= limite]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["hora"],
            y=df["velocidade_medida_global_media"],
            mode="lines+markers",
            name="Velocidade Média",
            line=dict(shape="spline", smoothing=1.2)
        )
    )

    fig.update_layout(
        title="Velocidade instantânea agregada por media",
        yaxis=dict(autorange=True),
        xaxis_title="Hora",
        yaxis_title="Velocidade medida [Emb/h]",
        template="plotly_dark",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(tickformat="%H:%M", showgrid=False)
    )

    return fig