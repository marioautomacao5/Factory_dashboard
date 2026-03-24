import pandas as pd
import streamlit as st

def aplicar_filtros(df_producao, df_paradas):

    # ======================================================
    # 🔹 PADRONIZAÇÃO DOS DFs
    # ======================================================
    df_producao = df_producao.copy()
    df_paradas  = df_paradas.copy()

    df_producao["LinhaProducao"] = df_producao["LinhaProducao"].str.strip().str.upper()

    if "Unidade" in df_paradas.columns:
        df_paradas["Unidade"] = df_paradas["Unidade"].str.strip().str.upper()

    if "Máquina" in df_paradas.columns:
        df_paradas["Máquina"] = pd.to_numeric(df_paradas["Máquina"], errors="coerce")

    # ======================================================
    # 🔹 VALORES ÚNICOS DIRETO DOS DFs
    # ======================================================
    unidades_disponiveis  = sorted(df_paradas["Unidade"].dropna().unique()) if "Unidade" in df_paradas.columns else []
    linhas_disponiveis    = sorted(df_producao["LinhaProducao"].dropna().unique())
    categorias_disponiveis = sorted(df_producao["Formato"].dropna().unique()) if "Formato" in df_producao.columns else []

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
        options=unidades_disponiveis,
        key="filtro_unidade"
    )

    if not unidades:
        unidades = unidades_disponiveis

    # Filtra paradas por unidade
    if "Unidade" in df_paradas.columns:
        df_paradas_filtrado = df_paradas[df_paradas["Unidade"].isin(unidades)]
    else:
        df_paradas_filtrado = df_paradas.copy()

    # Filtra linhas disponíveis após seleção de unidade
    if "Unidade" in df_paradas.columns and "Máquina" in df_paradas.columns:
        maquinas_filtradas = df_paradas_filtrado["Máquina"].dropna().unique()
        linhas_por_unidade = sorted(
            df_producao[df_producao["LinhaProducao"].isin(linhas_disponiveis)]["LinhaProducao"].unique()
        )
    else:
        linhas_por_unidade = linhas_disponiveis

    # ======================================================
    # 🔹 FILTRO CATEGORIA (Formato)
    # ======================================================
    categorias = st.sidebar.multiselect(
        "Categoria",
        options=categorias_disponiveis,
        key="filtro_categoria"
    )

    if not categorias:
        categorias = categorias_disponiveis

    # Filtra produção por categoria
    if "Formato" in df_producao.columns and categorias:
        df_producao_cat = df_producao[df_producao["Formato"].str.strip().str.upper().isin(
            [c.strip().upper() for c in categorias]
        )]
        linhas_por_categoria = sorted(df_producao_cat["LinhaProducao"].dropna().unique())
    else:
        linhas_por_categoria = linhas_por_unidade

    # Intersecção linhas disponíveis
    linhas_finais = sorted(set(linhas_por_unidade) & set(linhas_por_categoria)) or linhas_por_unidade

    # ======================================================
    # 🔹 FILTRO LINHA
    # ======================================================
    linhas = st.sidebar.multiselect(
        "Linha de produção",
        options=linhas_finais,
        key="filtro_linhas"
    )

    if not linhas:
        linhas = linhas_finais

    # ======================================================
    # 🔹 FILTRO PRODUÇÃO
    # ======================================================
    df_producao_filtrado = df_producao[
        df_producao["LinhaProducao"].isin(linhas)
    ]

    # ======================================================
    # 🔹 FILTRO PARADAS POR LINHA
    # ======================================================
    if "LinhaProducao" in df_paradas.columns:
        df_paradas["LinhaProducao"] = df_paradas["LinhaProducao"].str.strip().str.upper()
        df_paradas_filtrado = df_paradas[df_paradas["LinhaProducao"].isin(linhas)]
    elif "Unidade" in df_paradas.columns:
        df_paradas_filtrado = df_paradas[df_paradas["Unidade"].isin(unidades)]

    # ======================================================
    # 🔹 DEBUG OPCIONAL
    # ======================================================
    if st.sidebar.checkbox("Debug filtros"):
        st.write("Unidades disponíveis:",  unidades_disponiveis)
        st.write("Unidades selecionadas:", unidades)
        st.write("Categorias:",            categorias)
        st.write("Linhas:",                linhas)
        st.write("Produção filtrada:",     len(df_producao_filtrado))
        st.write("Paradas filtradas:",     len(df_paradas_filtrado))

    return df_producao_filtrado, df_paradas_filtrado