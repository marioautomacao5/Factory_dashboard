import pandas as pd
from datetime import timedelta

def inicio_turno_atual(agora):
    hora = agora.hour

    if 6 <= hora < 14:
        return agora.replace(hour=6, minute=0, second=0, microsecond=0)

    elif 14 <= hora < 22:
        return agora.replace(hour=14, minute=0, second=0, microsecond=0)

    else:
        if hora < 6:
            return (agora - pd.Timedelta(days=1)).replace(
                hour=22,
                minute=0,
                second=0,
                microsecond=0
            )
        else:
            return agora.replace(hour=22, minute=0, second=0, microsecond=0)

def calcular_metricas(df):

    def identificar_turno(ts):
        hora = ts.hour
        if 6 <= hora < 14:
            return "Turno 1"
        elif 14 <= hora < 22:
            return "Turno 2"
        else:
            return "Turno 3"

    # 🔹 DataFrame vazio
    if df.empty:
        return {
            "total_registros": 0,
            "linhas": 0,
            "oee_hora_atual": 0,
            "oee_hora_anterior": 0,
            "oee_turno": 0,
            "df_1h": pd.DataFrame(),
            "turno_atual": None,
            "inicio_turno": None,
            "producao_total_turno": 0,
            "producao_por_hora": pd.DataFrame(),
            "producao_hora_atual": 0,
            "producao_ultima_hora": 0,

            # ✅ NOVO
            "producao_total_turnoCx": 0,
            "producao_por_horaCx": pd.DataFrame(),
            "producao_hora_atualCx": 0,
            "producao_ultima_horaCx": 0
        }

    # 🔹 ordenação
    df = df.sort_values("timestamp")

    df["Dia"] = pd.to_datetime(df["Dia"]).dt.date

    # 🔹 cria hora GLOBAL
    df["hora"] = pd.to_datetime(
        df["Dia"].astype(str) + " " + df["HoraInicial"].astype(str),
        errors="coerce"
    )

    # 🔹 referência atual
    agora = df["timestamp"].max()

    # 🔹 turno atual
    inicio_turno = inicio_turno_atual(agora)
    df_turno = df[df["timestamp"] >= inicio_turno].copy()

    # 🔹 última hora (janela real)
    uma_hora = agora - timedelta(hours=1)
    df_1h = df[df["timestamp"] >= uma_hora]

    # ======================================================
    # 🔥 OEE POR HORA
    # ======================================================
    oee_por_hora = (
        df.sort_values("timestamp")
        .groupby(["LinhaProducao", "Dia", "hora"])
        .tail(1)
    )

    oee_por_hora = (
        oee_por_hora
        .groupby(["Dia", "hora"])["OEE"]
        .mean()
    )

    data_atual = agora.date()
    hora_atual = agora.floor("h")
    hora_anterior = hora_atual - pd.Timedelta(hours=1)

    oee_hora_atual = oee_por_hora.get((data_atual, hora_atual), 0)
    oee_hora_anterior = oee_por_hora.get((data_atual, hora_anterior), 0)

    # ======================================================
    # 🔥 OEE TURNO
    # ======================================================
    hora_inicio = inicio_turno.floor("h")
    dia_inicio = inicio_turno.date()

    if inicio_turno.hour == 22:
        oee_turno_filtrado = oee_por_hora[
            (
                (oee_por_hora.index.get_level_values("Dia") == dia_inicio) &
                (oee_por_hora.index.get_level_values("hora") >= hora_inicio)
            )
            |
            (
                (oee_por_hora.index.get_level_values("Dia") == data_atual) &
                (oee_por_hora.index.get_level_values("hora") <= hora_atual)
            )
        ]
    else:
        oee_turno_filtrado = oee_por_hora[
            (oee_por_hora.index.get_level_values("Dia") == data_atual) &
            (oee_por_hora.index.get_level_values("hora") >= hora_inicio) &
            (oee_por_hora.index.get_level_values("hora") <= hora_atual)
        ]

    oee_turno = oee_turno_filtrado.mean() if not oee_turno_filtrado.empty else 0

    # ======================================================
    # 🔥 PERDA DE RITMO GLOBAL (UNIDADE)
    # ======================================================

    perda_por_hora_global = (
        df
        .groupby(["LinhaProducao", "hora"])["PerdaRitmo"]
        .sum()
        .reset_index(name="PerdaHora")
        .sort_values("hora")
    )

    horas_perda = perda_por_hora_global["hora"].drop_duplicates().sort_values()

    if len(horas_perda) == 0:
        perda_hora_atual = 0
        perda_ultima_hora = 0
    else:
        hora_atual_perda = horas_perda.iloc[-1]
        hora_anterior_perda = horas_perda.iloc[-2] if len(horas_perda) > 1 else hora_atual_perda

        perda_hora_atual = (
            perda_por_hora_global
            .loc[perda_por_hora_global["hora"] == hora_atual_perda, "PerdaHora"]
            .sum()
        )

        perda_ultima_hora = (
            perda_por_hora_global
            .loc[perda_por_hora_global["hora"] == hora_anterior_perda, "PerdaHora"]
            .sum()
        )

    perda_por_hora_turno = (
        df_turno
        .groupby(["LinhaProducao", "hora"])["PerdaRitmo"]
        .sum()
        .reset_index(name="PerdaHora")
    )

    perda_total_turno = perda_por_hora_turno["PerdaHora"].sum()
    # ======================================================
    # 🔥 PRODUÇÃO GLOBAL (UNIDADE)
    # ======================================================
    producao_por_hora_global = (
        df
        .groupby(["LinhaProducao", "hora"])["ProducaoBruta"]
        .max()
        .reset_index(name="ProducaoHora")
        .sort_values("hora")
    )

    horas = producao_por_hora_global["hora"].drop_duplicates().sort_values()

    if len(horas) == 0:
        producao_hora_atual = 0
        producao_ultima_hora = 0
    else:
        hora_atual_prod = horas.iloc[-1]
        hora_anterior_prod = horas.iloc[-2] if len(horas) > 1 else hora_atual_prod

        producao_hora_atual = (
            producao_por_hora_global
            .loc[producao_por_hora_global["hora"] == hora_atual_prod, "ProducaoHora"]
            .sum()
        )

        producao_ultima_hora = (
            producao_por_hora_global
            .loc[producao_por_hora_global["hora"] == hora_anterior_prod, "ProducaoHora"]
            .sum()
        )

    # ======================================================
    # 🔥 PRODUÇÃO GLOBAL (CAIXAS)
    # ======================================================
    producao_por_hora_global_cx = (
        df
        .groupby(["LinhaProducao", "hora"])["ProducaoBrutaCx"]
        .max()
        .reset_index(name="ProducaoHoraCx")
        .sort_values("hora")
    )

    horas_cx = producao_por_hora_global_cx["hora"].drop_duplicates().sort_values()

    if len(horas_cx) == 0:
        producao_hora_atual_cx = 0
        producao_ultima_hora_cx = 0
    else:
        hora_atual_prod_cx = horas_cx.iloc[-1]
        hora_anterior_prod_cx = horas_cx.iloc[-2] if len(horas_cx) > 1 else hora_atual_prod_cx

        producao_hora_atual_cx = (
            producao_por_hora_global_cx
            .loc[producao_por_hora_global_cx["hora"] == hora_atual_prod_cx, "ProducaoHoraCx"]
            .sum()
        )

        producao_ultima_hora_cx = (
            producao_por_hora_global_cx
            .loc[producao_por_hora_global_cx["hora"] == hora_anterior_prod_cx, "ProducaoHoraCx"]
            .sum()
        )

    # ======================================================
    # 🔥 PRODUÇÃO TURNO (UNIDADE)
    # ======================================================
    producao_por_hora_turno = (
        df_turno
        .groupby(["LinhaProducao", "hora"])["ProducaoBruta"]
        .max()
        .reset_index(name="ProducaoHora")
    )

    total_producao = producao_por_hora_turno["ProducaoHora"].sum()

    # ======================================================
    # 🔥 PRODUÇÃO TURNO (CAIXAS)
    # ======================================================
    producao_por_hora_turno_cx = (
        df_turno
        .groupby(["LinhaProducao", "hora"])["ProducaoBrutaCx"]
        .max()
        .reset_index(name="ProducaoHoraCx")
    )

    total_producao_cx = producao_por_hora_turno_cx["ProducaoHoraCx"].sum()

    # ======================================================
    # 🔥 VELOCIDADE MEDIDA DA LINHA
    # ======================================================

    df_sorted = df.sort_values("HoraFinal")

    # 2️⃣ Agrupar e pegar o último CicloMedio de cada Linha/Hora
    velocidade_medida_global = (
        df_sorted
        .groupby(["LinhaProducao", "hora"])["CicloMedio"]
        .last()  # pega o último valor após ordenar por HoraFinal
        .reset_index(name="CicloMedio_global")
    )

    velocidade_medida_global["CicloMedio_global"] = pd.to_numeric(
        velocidade_medida_global["CicloMedio_global"],
        errors="coerce"
    )

    # 2️⃣ Calcular peças por segundo
    velocidade_medida_global["pecas_por_segundo_global"] = (1 / velocidade_medida_global["CicloMedio_global"]) * 1000

    # 3️⃣ Calcular velocidade medida global
    velocidade_medida_global["velocidade_medida_global"] = velocidade_medida_global["pecas_por_segundo_global"] * 3600

    velocidade_medida_global["velocidade_medida_global"] = (
        velocidade_medida_global["velocidade_medida_global"]
        .replace([float("inf"), -float("inf")], 0)
        .fillna(0)
    )

    # 4️⃣ Criar DataFrame da soma por hora
    velocidade_soma = (
        velocidade_medida_global
        .groupby("hora")["velocidade_medida_global"]
        .sum()
        .reset_index()
        .rename(columns={"velocidade_medida_global": "velocidade_medida_global_soma"})
    )

    # 5️⃣ Criar DataFrame da média por hora
    velocidade_media = (
        velocidade_medida_global
        .groupby("hora")["velocidade_medida_global"]
        .mean()
        .reset_index()
        .rename(columns={"velocidade_medida_global": "velocidade_medida_global_media"})
    )

    # ======================================================
    # 🔹 META OEE MÉDIA (filtrada)
    # ======================================================
    if "Meta_OEE" in df.columns:
        meta_oee_filtrada = df["Meta_OEE"].mean()
    else:
        meta_oee_filtrada = 85.0  # default se a coluna não existir

    # ======================================================
    # 🔹 RETORNO FINAL
    # ======================================================
    return {
        "total_registros": len(df),
        "linhas": df["LinhaProducao"].nunique(),

        "oee_hora_atual": oee_hora_atual,
        "oee_hora_anterior": oee_hora_anterior,
        "oee_turno": oee_turno,

        "df_1h": df_1h,
        "turno_atual": identificar_turno(agora),
        "inicio_turno": inicio_turno,

         # 🔹 RITMO
        "perda_total_turno": perda_total_turno,
        "perda_hora_atual": perda_hora_atual,
        "perda_ultima_hora": perda_ultima_hora,

        # 🔹 UNIDADE
        "producao_total_turno": total_producao,
        "producao_por_hora": producao_por_hora_turno,
        "producao_hora_atual": producao_hora_atual,
        "producao_ultima_hora": producao_ultima_hora,

        # 🔹 CAIXAS
        "producao_total_turnoCx": total_producao_cx,
        "producao_por_horaCx": producao_por_hora_turno_cx,
        "producao_hora_atualCx": producao_hora_atual_cx,
        "producao_ultima_horaCx": producao_ultima_hora_cx,

        "Velocidade_nominal_individual": velocidade_medida_global,
        "velocidade_medida_global_soma": velocidade_soma,
        "velocidade_medida_global_media": velocidade_media,

        "meta_oee_filtrada": meta_oee_filtrada,
    }