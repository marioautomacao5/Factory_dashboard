import plotly.express as px


def heatmap_linha_hora(df):

    pivot = df.pivot_table(
        values="OEE",
        index="LinhaProducao",
        columns="Hora",
        aggfunc="mean"
    )

    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale="RdYlGn",
        title="OEE Linha x Hora"
    )

    return fig