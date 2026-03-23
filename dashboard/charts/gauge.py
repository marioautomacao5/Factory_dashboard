import plotly.graph_objects as go

def gauge_oee(valor, meta_oee=85.0):
    # eixo fixo de 0 até 120% da meta ou 100%, o que for maior
    max_axis = max(100, meta_oee * 1.2, valor * 1.1)

    steps = [
        {"range": [0, 0.95 * meta_oee], "color": "#ff4d4d"},       # vermelho abaixo de 95% da meta
        {"range": [0.95 * meta_oee, 1.05 * meta_oee], "color": "#ffd11a"}, # amarelo +/-5%
        {"range": [1.05 * meta_oee, max_axis], "color": "#3cff00"}, # verde acima da meta
    ]

    threshold = {
        "line": {"color": "red", "width": 4},
        "thickness": 0.75,
        "value": meta_oee
    }

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=valor,
            title={"text": "OEE do turno atual"},
            gauge={
                "axis": {"range": [0, max_axis]},
                "steps": steps,
                "threshold": threshold
            }
        )
    )

    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig