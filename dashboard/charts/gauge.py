import plotly.graph_objects as go

def gauge_oee(valor, meta_oee=85.0):
    # eixo fixo de 0 até 120% da meta ou 100%, o que for maior
    max_axis = max(100, meta_oee * 1.2, valor * 1.1)

    steps = [
        {"range": [0, 0.95 * meta_oee], "color": "#ff4d4d"},      # Vermelho
        {"range": [0.95 * meta_oee, 1.05 * meta_oee], "color": "#ffd11a"}, # Amarelo
        {"range": [1.05 * meta_oee, max_axis], "color": "#3cff00"}, # Verde
    ]

    threshold = {
        "line": {"color": "white", "width": 4}, # Mudei para branco para destacar no fundo escuro
        "thickness": 0.75,
        "value": meta_oee
    }

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=valor,
            title={"text": "Current Shift OEE", "font": {"color": "white", "size": 18}},
            number={"font": {"color": "white"}}, # Cor do número central
            gauge={
                "axis": {
                    "range": [0, max_axis],
                    "tickcolor": "white", # Cor dos tracinhos da escala
                    "tickfont": {"color": "white"} # Cor dos números da escala
                },
                "steps": steps,
                "threshold": threshold,
                "bar": {"color": "#2c3e50"} # Cor do ponteiro (ajuste se necessário)
            }
        )
    )

    # A MÁGICA PARA O STREAMLIT CLOUD ESTÁ AQUI:
    fig.update_layout(
        height=250,
        margin=dict(l=30, r=30, t=50, b=20),
        paper_bgcolor='rgba(0,0,0,0)', # Fundo do papel transparente
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo do gráfico transparente
        font_color="white"             # Força todas as fontes para branco
    )

    return fig