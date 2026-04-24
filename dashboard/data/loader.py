from pathlib import Path
from datetime import datetime, timedelta
import time
import duckdb
import pandas as pd
import streamlit as st
import os

# ======================================================
# 📁 PATH DO BANCO
# ======================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "warehouse" / "producao.duckdb"

METAS_PATH = BASE_DIR / "data" / "metas.csv"

# ======================================================
# 🔍 VERIFICA SE TABELA EXISTE
# ======================================================

def tabela_existe(con, nome_tabela):
    tabelas = con.execute("SHOW TABLES").fetchall()
    tabelas = [t[0] for t in tabelas]
    return nome_tabela in tabelas

# ======================================================
# 🔄 CURSOR DE TEMPO SIMULADO (modo portfólio)
# Lê o range do histórico uma vez por hora e devolve um
# "agora simulado" que avança em tempo real sobre os dados,
# reiniciando no início quando chega ao fim.
# ======================================================

@st.cache_data(ttl=3600)
def _get_range_historico():
    if not DB_PATH.exists():
        return None, None
    try:
        con = duckdb.connect(str(DB_PATH), read_only=True)
        tabelas = [t[0] for t in con.execute("SHOW TABLES").fetchall()]

        if "producao_historico" not in tabelas:
            con.close()
            return None, None

        row = con.execute("""
            SELECT
                MIN(CAST(Dia AS DATE)) AS data_min,
                MAX(CAST(Dia AS DATE)) AS data_max
            FROM producao_historico
        """).fetchone()
        con.close()
        return row[0], row[1]
    except Exception:
        return None, None


def get_tempo_simulado():
    """
    Retorna um datetime que avança em tempo real sobre o histórico e
    reinicia automaticamente ao atingir o fim.
    """
    data_min, data_max = _get_range_historico()
    if data_min is None or data_max is None:
        return None

    dt_min = datetime.combine(data_min, datetime.min.time())
    dt_max = datetime.combine(data_max, datetime.max.time().replace(microsecond=0))

    range_seconds = (dt_max - dt_min).total_seconds()
    if range_seconds <= 0:
        return dt_max

    offset = time.time() % range_seconds
    return dt_min + timedelta(seconds=offset)

# ======================================================
# 📊 PRODUÇÃO
# ======================================================

@st.cache_data(ttl=60)
def carregar_dados():

    def formatar_duracao(segundos):
        if pd.isna(segundos):
            return None
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segundos = int(segundos % 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    if not DB_PATH.exists():
        return pd.DataFrame()

    try:
        con = duckdb.connect(str(DB_PATH), read_only=True)

        # --------------------------------------------------
        # Modo simulado: usa historico com janela deslizante
        # Fallback: consulta (ETL rodando localmente)
        # --------------------------------------------------
        if tabela_existe(con, "producao_historico"):
            tempo_simulado = get_tempo_simulado()
            if tempo_simulado is not None:
                dia_fim   = tempo_simulado.date()
                dia_inicio = (tempo_simulado - timedelta(days=2)).date()
                query_table = "producao_historico"
                where_clause = "WHERE CAST(Dia AS DATE) BETWEEN ? AND ?"
                params = [str(dia_inicio), str(dia_fim)]
            else:
                query_table = "producao_historico"
                where_clause = ""
                params = []
        elif tabela_existe(con, "producao_consulta"):
            query_table = "producao_consulta"
            where_clause = ""
            params = []
        else:
            st.warning("Nenhuma tabela de produção encontrada.")
            con.close()
            return pd.DataFrame()

        df = con.execute(f"""
            SELECT
                Dia,
                LinhaProducao,
                HoraInicial,
                HoraFinal,
                OEE,
                Produto,
                Formato,
                CicloPadrao,
                CicloMedio,
                MetaHoraSistema,
                ProducaoBruta,
                ProducaoBrutaCx,
                Paradas,
                TempoTotalParada,
                PerdaRitmo,
                DataCarga,
                EXTRACT(EPOCH FROM CAST(TempoTotalParada AS INTERVAL)) AS TempoTotalParada_segundos
            FROM {query_table}
            {where_clause}
            ORDER BY Dia DESC, HoraFinal DESC
        """, params).df()

        con.close()

        # ======================================================
        # 🧹 LIMPEZA
        # ======================================================
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace("\ufeff", "", regex=False)

        # ======================================================
        # 🆕 GARANTIR CAMPOS
        # ======================================================
        if "Formato" not in df.columns:
            df["Formato"] = None

        if "ProducaoBrutaCx" not in df.columns:
            df["ProducaoBrutaCx"] = 0

        # ======================================================
        # 🔢 TIPAGEM
        # ======================================================
        df["ProducaoBruta"] = pd.to_numeric(df["ProducaoBruta"], errors="coerce")
        df["ProducaoBrutaCx"] = pd.to_numeric(df["ProducaoBrutaCx"], errors="coerce")
        df["MetaHoraSistema"] = pd.to_numeric(df["MetaHoraSistema"], errors="coerce")
        df["OEE"] = pd.to_numeric(df["OEE"], errors="coerce")

        # ======================================================
        # 🕒 DATAS
        # ======================================================
        df["Dia"] = pd.to_datetime(df["Dia"], errors="coerce").dt.date

        #df["HoraInicial"] = pd.to_datetime(df["HoraInicial"], errors="coerce")
        #df["HoraFinal"] = pd.to_datetime(df["HoraFinal"], errors="coerce")

        # ✅ TIMESTAMP (ESSENCIAL)
        df["timestamp"] = pd.to_datetime(
            df["Dia"].astype(str) + " " + df["HoraFinal"].astype(str),
            errors="coerce"
        )

        # ======================================================
        # ⏱️ TEMPO PARADA FORMATADO
        # ======================================================
        if "TempoTotalParada_segundos" in df.columns:
            df["TempoTotalParada"] = df["TempoTotalParada_segundos"].apply(formatar_duracao)

        df["PerdaRitmo_fmt"] = pd.to_timedelta(df["PerdaRitmo"], unit="s")

        return df

    except Exception as e:
        st.warning(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()


# ======================================================
# 🛑 PARADAS
# ======================================================

@st.cache_data(ttl=60)
def carregar_paradas():

    def formatar_duracao(segundos):
        if pd.isna(segundos):
            return None
        horas = int(segundos // 3600)
        minutos = int((segundos % 3600) // 60)
        segundos = int(segundos % 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    if not DB_PATH.exists():
        return pd.DataFrame()

    try:
        con = duckdb.connect(str(DB_PATH), read_only=True)

        # --------------------------------------------------
        # Modo simulado: usa historico com janela deslizante
        # Fallback: consulta (ETL rodando localmente)
        # --------------------------------------------------
        if tabela_existe(con, "paradas_historico"):
            tempo_simulado = get_tempo_simulado()
            if tempo_simulado is not None:
                dt_fim    = tempo_simulado
                dt_inicio = tempo_simulado - timedelta(days=2)
                query_table  = "paradas_historico"
                where_clause = 'WHERE "Inicio" BETWEEN ? AND ?'
                params = [str(dt_inicio), str(dt_fim)]
            else:
                query_table  = "paradas_historico"
                where_clause = ""
                params = []
        elif tabela_existe(con, "paradas_consulta"):
            query_table  = "paradas_consulta"
            where_clause = ""
            params = []
        else:
            st.warning("Nenhuma tabela de paradas encontrada.")
            con.close()
            return pd.DataFrame()

        df = con.execute(f"""
            SELECT
                *,
                TRY_CAST("Duração" AS INTERVAL) AS duracao_interval,
                EXTRACT(EPOCH FROM TRY_CAST("Duração" AS INTERVAL)) AS duracao_segundos
            FROM {query_table}
            {where_clause}
            ORDER BY "Inicio" DESC
        """, params).df()

        con.close()

        # ======================================================
        # 🧹 LIMPEZA
        # ======================================================
        df.columns = df.columns.str.strip()
        df.columns = df.columns.str.replace("\ufeff", "", regex=False)

        # ======================================================
        # 🔄 DATETIME
        # ======================================================
        if "Inicio" in df.columns:
            df["Inicio"] = pd.to_datetime(df["Inicio"], errors="coerce")

        if "Fim" in df.columns:
            df["Fim"] = pd.to_datetime(df["Fim"], errors="coerce")

        # ======================================================
        # ⏱️ DURAÇÃO FORMATADA
        # ======================================================
        if "duracao_segundos" in df.columns:
            df["Duração"] = df["duracao_segundos"].apply(formatar_duracao)

        return df

    except Exception as e:
        st.warning(f"Erro ao carregar paradas: {e}")
        return pd.DataFrame()


# ======================================================
# 🔹 FUNÇÃO PARA CARREGAR METAS COM MONITORAMENTO DE ARQUIVO
# ======================================================
def carregar_metas():
    """
    Carrega metas de OEE a partir do CSV.
    Usa a data de modificação do arquivo como hash do cache.
    Se o arquivo for alterado, o cache é invalidado automaticamente.
    """
    # Pega a data de modificação do arquivo
    mtime = os.path.getmtime(METAS_PATH) if METAS_PATH.exists() else 0

    @st.cache_data(ttl=0, hash_funcs={float: lambda _: mtime})
    def _carregar():
        if METAS_PATH.exists():
            df_metas = pd.read_csv(METAS_PATH, sep=";")
        else:
            df_metas = pd.DataFrame(columns=["ID_Linha", "LinhaProducao", "Meta_OEE", "DataAlteracao"])

        # Garante a coluna Meta_OEE
        if "Meta_OEE" not in df_metas.columns:
            df_metas["Meta_OEE"] = 85.0

        df_metas["Meta_OEE"] = pd.to_numeric(df_metas["Meta_OEE"], errors="coerce").fillna(85.0)

        # Garante coluna de data da alteração
        if "DataAlteracao" not in df_metas.columns:
            df_metas["DataAlteracao"] = pd.NaT

        return df_metas

    return _carregar()


# ======================================================
# 🔹 FUNÇÃO PARA SINCRONIZAR METAS COM DADOS DE PRODUÇÃO
# ======================================================
def aplicar_metas(df_producao):
    """
    Recebe df de produção e adiciona a coluna Meta_OEE
    baseada na linha de produção.
    Detecta alterações no CSV automaticamente.
    """
    df_metas = carregar_metas()

    if df_producao.empty:
        df_producao["Meta_OEE"] = 0
        return df_producao

    # Padroniza nomes para merge
    df_producao["LinhaProducao"] = df_producao["LinhaProducao"].astype(str).str.strip().str.upper()
    df_metas["LinhaProducao"] = df_metas["LinhaProducao"].astype(str).str.strip().str.upper()

    # Merge com left join (todas as linhas de produção do df_producao)
    df = df_producao.merge(
        df_metas[["LinhaProducao", "Meta_OEE", "DataAlteracao"]],
        on="LinhaProducao",
        how="left"
    )

    # Caso alguma linha não tenha meta definida, colocar valor default
    df["Meta_OEE"] = df["Meta_OEE"].fillna(85.0)

    # Se não houver data de alteração, preenche com NaT
    df["DataAlteracao"] = df["DataAlteracao"].fillna(pd.NaT)

    return df