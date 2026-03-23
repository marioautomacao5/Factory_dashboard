import pandas as pd


def preparar_dados(df):

    if df.empty:
        return df

    df = df.copy()

    df["Dia"] = pd.to_datetime(df["Dia"], errors="coerce")

    df["OEE"] = pd.to_numeric(df["OEE"], errors="coerce")

    df["timestamp"] = pd.to_datetime(
        df["Dia"].dt.strftime("%Y-%m-%d") + " " + df["HoraFinal"].astype(str),
        errors="coerce"
    )

    df["Hora"] = df["timestamp"].dt.hour

    return df