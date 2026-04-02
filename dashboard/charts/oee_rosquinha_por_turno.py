import plotly.express as px

def rosquinha_turnos(df):
    def turno(h):
        if 6 <= h < 14:
            return "Turno 1"
        if 14 <= h < 22:
            return "Turno 2"
        return "Turno 3"

    # Criando a coluna de turno (Idealmente isso deve ser feito antes do gráfico para performance)
    df["Turno"] = df["Hora"].apply(turno)
    turno_df = df.groupby("Turno")["OEE"].mean().reset_index()

    fig = px.pie(
        turno_df,
        names="Shift",
        values="OEE",
        hole=0.5,
        title="OEE by Shift",
        # Definindo cores fixas para os turnos (opcional, mas ajuda na consistência)
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_traces(
        textinfo="label+percent",
        hoverinfo="label+value+percent",
        textfont=dict(
            color="white",
            size=14,
            family="Arial Black"
        ),
        marker=dict(line=dict(color='#0e1117', width=2)) # Linha separadora entre as fatias
    )

    fig.update_layout(
        # Forçar transparência para herdar o fundo do Streamlit
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color="white",
        
        title={
            "text": "OEE by Shift",
            "y": 0.95,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 20, "color": "white"}
        },
        
        template="plotly_dark",
        height=450,
        margin=dict(l=20, r=20, t=100, b=80),

        # Legenda horizontal na parte inferior
        legend=dict(
            title_text="", # Removi o título da legenda para ganhar espaço
            x=0.5,
            y=-0.1,
            xanchor="center",
            yanchor="top",
            orientation="h",
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=12, color="white")
        )
    )

    return fig