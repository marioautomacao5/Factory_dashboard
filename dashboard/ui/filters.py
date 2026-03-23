import pandas as pd
import streamlit as st

def aplicar_filtros(df_producao, df_paradas):

    # ======================================================
    # 🔹 MAPEAMENTO COMPLETO
    # ======================================================
    mapa = pd.DataFrame({
        "Unidade": [
            "Araguari","Araguari","Araguari","Araguari","Araguari",
            "Astolfo Dutra","Astolfo Dutra","Astolfo Dutra","Astolfo Dutra","Astolfo Dutra",
            "Aracati","Aracati","Aracati","Aracati"
        ],
        "Máquina": [30,35,36,37,49,78,79,80,89,91,1,5,8,16],
        "LinhaProducao": [
            "PET","SIG I","SIG II","SIG III","SIG IV",
            "PET ZEGLA","LINHA TETRA 1000 ML","LINHA-TETRA-200",
            "LINHA SIG 1000 ML","LINHA DE ENVASE PPB SIG 200ML",
            "PET 500/1000ml","SIG 200/150ML - CFA 112",
            "SIG 1000/750ML","SIG 200/150ML - CFA 124"
        ],
        "Categoria": [
            "PET","PPB Litro","PPB Litro","Kids","Kids",
            "PET","PPB Litro","Kids","PPB Litro","Kids",
            "PET","Kids","PPB Litro","Kids"
        ]
    })

    # ======================================================
    # 🔹 PADRONIZAÇÃO
    # ======================================================
    for col in ["LinhaProducao", "Unidade", "Categoria"]:
        mapa[col] = mapa[col].str.strip().str.upper()

    df_producao["LinhaProducao"] = df_producao["LinhaProducao"].str.strip().str.upper()
    df_paradas["Máquina"] = pd.to_numeric(df_paradas["Máquina"], errors="coerce")
    mapa["Máquina"] = pd.to_numeric(mapa["Máquina"], errors="coerce")

    # ======================================================
    # 🔹 SESSION STATE
    # ======================================================
    for key in ["filtro_unidade", "filtro_categoria", "filtro_linhas"]:
        if key not in st.session_state:
            st.session_state[key] = []

    # ======================================================
    # 🔹 FILTRO UNIDADE
    # ======================================================
    unidades = st.sidebar.multiselect(
        "Unidade",
        options=sorted(mapa["Unidade"].unique()),
        key="filtro_unidade"
    )

    if not unidades:
        unidades = list(mapa["Unidade"].unique())

    mapa_filtrado = mapa[mapa["Unidade"].isin(unidades)]

    # ======================================================
    # 🔹 FILTRO CATEGORIA
    # ======================================================
    categorias = st.sidebar.multiselect(
        "Categoria",
        options=sorted(mapa_filtrado["Categoria"].unique()),
        key="filtro_categoria"
    )

    if not categorias:
        categorias = list(mapa_filtrado["Categoria"].unique())

    mapa_filtrado = mapa_filtrado[
        mapa_filtrado["Categoria"].isin(categorias)
    ]

    # ======================================================
    # 🔹 FILTRO LINHA
    # ======================================================
    linhas = st.sidebar.multiselect(
        "Linha de produção",
        options=sorted(mapa_filtrado["LinhaProducao"].unique()),
        key="filtro_linhas"
    )

    if not linhas:
        linhas = list(mapa_filtrado["LinhaProducao"].unique())

    mapa_filtrado = mapa_filtrado[
        mapa_filtrado["LinhaProducao"].isin(linhas)
    ]

    # ======================================================
    # 🔹 FILTRO PRODUÇÃO
    # ======================================================
    df_producao_filtrado = df_producao[
        df_producao["LinhaProducao"].isin(mapa_filtrado["LinhaProducao"])
    ]

    # ======================================================
    # 🔹 FILTRO PARADAS
    # ======================================================
    df_paradas_filtrado = df_paradas[
        df_paradas["Máquina"].isin(mapa_filtrado["Máquina"])
    ]

    # ======================================================
    # 🔹 DEBUG OPCIONAL
    # ======================================================
    if st.sidebar.checkbox("Debug filtros"):
        st.write("Unidades:", unidades)
        st.write("Categorias:", categorias)
        st.write("Linhas:", linhas)
        st.write("Máquinas:", mapa_filtrado["Máquina"].tolist())

    return df_producao_filtrado, df_paradas_filtrado