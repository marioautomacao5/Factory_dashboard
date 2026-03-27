import plotly.express as px

def grafico_turno(df):
    def turno(h):
        if 6 <= h < 14:
            return "Turno 1"
        if 14 <= h < 22:
            return "Turno 2"
        return "Turno 3"

    # Criando a coluna de turno
    df["Turno"] = df["Hora"].apply(turno)
    turno_df = df.groupby("Turno")["OEE"].mean().reset_index()

    # Criando o gráfico de barras
    fig = px.bar(
        turno_df,
        x="Turno",
        y="OEE",
        title="OEE por Turno",
        text_auto='.2f', # Exibe o valor do OEE em cima da barra com 2 casas decimais
        color="Turno",   # Dá uma cor diferente para cada turno
        color_discrete_sequence=px.colors.qualitative.Safe # Paleta de cores visível no escuro
    )

    fig.update_traces(
        textfont_size=12, 
        textangle=0, 
        textposition="outside", 
        cliponaxis=False
    )

    # Configurações de Tema para Streamlit Cloud
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        
        title={
            "text": "OEE Médio por Turno",
            "font": {"size": 20, "color": "white"},
            "x": 0.5,
            "xanchor": "center"
        },

        xaxis=dict(
            title="Turnos de Produção",
            gridcolor="#2d323e",
            tickfont=dict(color="white")
        ),

        yaxis=dict(
            title="OEE (%)",
            gridcolor="#2d323e",
            zerolinecolor="#2d323e",
            tickfont=dict(color="white"),
            range=[0, 115] # Espaço extra para o texto acima da barra não cortar
        ),

        showlegend=False, # Como o eixo X já diz o turno, a legenda é opcional
        height=400,
        margin=dict(l=20, r=20, t=60, b=40)
    )

    return fig