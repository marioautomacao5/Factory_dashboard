import plotly.express as px

def rosquinha_turnos(df):

    def turno(h):

        if 6 <= h < 14:
            return "Turno 1"

        if 14 <= h < 22:
            return "Turno 2"

        return "Turno 3"

    df["Turno"] = df["Hora"].apply(turno)

    turno_df = df.groupby("Turno")["OEE"].mean().reset_index()

    fig = px.pie(
        turno_df,
        names="Turno",
        values="OEE",
        hole=0.5,
        title="OEE por Turno"
    )

    fig.update_traces(
        textinfo="label+percent",
        textfont=dict(
            color="white",
            size=14,
            family="Arial Black"
        )
    )

    fig.update_layout(
        legend_title="Turnos",
        template="plotly_dark",
        height=450,   # altura
        margin=dict(l=20, r=20, t=90, b=30),

        # 👇 posição da legenda
        legend=dict(
            x=0.5,          # centralizada
            y=-0.25,          # baixo
            xanchor="center",
            yanchor="bottom",
            orientation="h",  # horizontal
            #font=dict(size=10),
            bgcolor="rgba(0,0,0,0)",  # 👈 fundo transparente
            borderwidth=0
        )
    )

    return fig