import plotly.express as px


def grafico_turno(df):

    def turno(h):

        if 6 <= h < 14:
            return "Turno 1"

        if 14 <= h < 22:
            return "Turno 2"

        return "Turno 3"

    df["Turno"] = df["Hora"].apply(turno)

    turno_df = df.groupby("Turno")["OEE"].mean().reset_index()

    fig = px.bar(
        turno_df,
        x="Turno",
        y="OEE",
        title="OEE por Turno"
    )

    return fig