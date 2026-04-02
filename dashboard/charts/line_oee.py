import plotly.graph_objects as go

def linha_oee(df, meta_oee=None):
    # calcula média de OEE por timestamp
    df_media = (
        df.groupby("timestamp", as_index=False)["OEE"]
        .mean()
        .sort_values("timestamp")
    )

    fig = go.Figure()

    # Linha principal de OEE
    fig.add_trace(
        go.Scatter(
            x=df_media["timestamp"],
            y=df_media["OEE"],
            mode="lines+markers",
            name="Average OEE",
            line=dict(shape="spline", smoothing=1.2, color="#636EFA"), # Azul vibrante para destacar no escuro
            marker=dict(size=6)
        )
    )

    # Linha tracejada da meta
    if meta_oee is not None:
        fig.add_trace(
            go.Scatter(
                x=df_media["timestamp"],
                y=[meta_oee] * len(df_media),
                mode="lines",
                name="OEE target",
                line=dict(color="#EF553B", width=2, dash="dash") # Vermelho mais visível no dark
            )
        )

    # AJUSTES DE TEMA E TRANSPARÊNCIA
    fig.update_layout(
        title={
            "text": "Real-Time OEE",
            "font": {"color": "white", "size": 18}
        },
        # Transparência total do fundo
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white", # Força todos os textos (legendas e eixos) para branco
        
        # Configuração dos Eixos
        xaxis=dict(
            title="Hora",
            gridcolor="#2d323e", # Cor da grade suave (dark grey)
            zerolinecolor="#2d323e",
            tickfont=dict(color="white")
        ),
        yaxis=dict(
            title="OEE (%)",
            autorange=True,
            gridcolor="#2d323e",
            zerolinecolor="#2d323e",
            tickfont=dict(color="white")
        ),
        
        legend=dict(
            font=dict(color="white"),
            bgcolor="rgba(0,0,0,0)" # Fundo da legenda transparente
        ),
        
        height=350,
        margin=dict(l=30, r=20, t=60, b=40)
    )

    return fig