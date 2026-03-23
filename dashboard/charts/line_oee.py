import plotly.graph_objects as go


def linha_oee(df, meta_oee=None):

    # calcula média de OEE por timestamp
    df_media = (
        df.groupby("timestamp", as_index=False)["OEE"]
        .mean()
        .sort_values("timestamp")
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_media["timestamp"],
            y=df_media["OEE"],
            mode="lines+markers",
            name="OEE Médio",
            line=dict(shape="spline", smoothing=1.2)
        )
    )

    # linha tracejada da meta
    if meta_oee is not None:
        fig.add_trace(
            go.Scatter(
                x=df_media["timestamp"],
                y=[meta_oee] * len(df_media),
                mode="lines",
                name="Meta OEE",
                line=dict(color="red", width=2, dash="dash")
            )
        )

    fig.update_layout(
        title="OEE instantâneo",
        yaxis=dict(autorange=True),
        xaxis_title="Hora",
        yaxis_title="OEE (%)",
        height=350,   # altura
        margin=dict(l=20, r=20, t=50, b=20)

    )

    return fig