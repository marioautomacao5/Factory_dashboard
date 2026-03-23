import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime
import duckdb
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed

# ======================================================
# CONFIGURAÇÕES
# ======================================================

usuario = "dash.paradas"
senha = "Ebba@123456789"

LOGIN_URL = "https://prodwin.ebba.com.br/Usuario.Login.aspx?cmd=logout"
RELATORIO_URL = "https://prodwin.ebba.com.br/report/default/parada/OcorrenciaParada.aspx"

DATA_RELATORIO_SITE = datetime.now().strftime("%d/%m/%Y")

# ======================================================
# ESTRUTURA DE PASTAS
# ======================================================

BASE_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_RAW = os.path.join(BASE_PROJETO, "data", "raw")
DATA_XLSX = os.path.join(DATA_RAW, "xlsx_paradas")
DATA_WAREHOUSE = os.path.join(BASE_PROJETO, "data", "warehouse")
LOG_DIR = os.path.join(BASE_PROJETO, "logs")

os.makedirs(DATA_RAW, exist_ok=True)
os.makedirs(DATA_XLSX, exist_ok=True)
os.makedirs(DATA_WAREHOUSE, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

ARQ_LOG = os.path.join(LOG_DIR, "pipeline_paradas.log")

DB_CONSULTA = os.path.join(DATA_WAREHOUSE, "producao.duckdb")

# ======================================================
# TURNO ATUAL
# ======================================================

def obter_turno_atual():

    agora = datetime.now().time()

    # ajuste os horários se necessário
    if agora >= datetime.strptime("06:00","%H:%M").time() and agora < datetime.strptime("14:00","%H:%M").time():
        return "1"

    elif agora >= datetime.strptime("14:00","%H:%M").time() and agora < datetime.strptime("22:00","%H:%M").time():
        return "2"

    else:
        return "3"

# ======================================================
# LOG
# ======================================================

def registrar_log(msg):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    linha = f"[{timestamp}] {msg}"

    print(linha)

    with open(ARQ_LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

# ======================================================
# LIMPEZA DE ARQUIVOS ANTIGOS
# ======================================================

def limpar_xlsx_antigos(dias=15):

    limite = time.time() - dias * 86400

    for arq in os.listdir(DATA_XLSX):

        caminho = os.path.join(DATA_XLSX, arq)

        if os.path.getmtime(caminho) < limite:
            os.remove(caminho)

# ======================================================
# SALVAR RELATÓRIO BRUTO
# ======================================================

def salvar_xlsx_bruto(conteudo, grupo):

    try:

        nome = f"grupo_{grupo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        caminho = os.path.join(DATA_XLSX, nome)

        df = pd.read_excel(BytesIO(conteudo), header=None)

        df.to_csv(caminho, sep=";", index=False, encoding="utf-8-sig")

    except Exception as e:

        registrar_log(f"Erro salvando CSV bruto grupo {grupo}: {e}")

# ======================================================
# LOGIN
# ======================================================

def login(session):

    headers = {"User-Agent": "Mozilla/5.0"}

    r = session.get(LOGIN_URL, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    viewstate = soup.find("input", {"name": "__VIEWSTATE"})["value"]
    viewstategenerator = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]

    payload = {
        "__VIEWSTATE": viewstate,
        "__VIEWSTATEGENERATOR": viewstategenerator,
        "txtUsuario": usuario,
        "txtSenha": senha,
        "cbLanguage": "1",
        "Button1": "OK"
    }

    session.post(LOGIN_URL, headers=headers, data=payload)

# ======================================================
# OBTER PARAMETROS DA PAGINA
# ======================================================

def obter_params_relatorio(session):

    headers = {"User-Agent": "Mozilla/5.0"}

    r = session.get(RELATORIO_URL, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    def get_value(nome):

        campo = soup.find("input", {"name": nome})

        return campo["value"] if campo else ""

    params = {
        "__VIEWSTATE": get_value("__VIEWSTATE"),
        "__VIEWSTATEGENERATOR": get_value("__VIEWSTATEGENERATOR"),
        "__EVENTVALIDATION": get_value("__EVENTVALIDATION")
    }

    #registrar_log(f"VIEWSTATE capturado: {len(params['__VIEWSTATE'])} caracteres")

    return params

def extrair_cd_paradas(session):

    headers = {"User-Agent": "Mozilla/5.0"}

    r = session.get(RELATORIO_URL, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")

    cd_false = []
    cd_true = []

    # pega TODOS inputs da página
    inputs = soup.find_all("input")

    for inp in inputs:

        name = inp.get("name", "")
        value = inp.get("value", "")

        # padrão ASP.NET checkbox list
        if name.startswith("cdParada_"):

            if "True" in name:
                cd_true.append(value)
            else:
                cd_false.append(value)

    #registrar_log(f"cdParada extraído: {len(cd_true)} true / {len(cd_false)} false")

    return cd_true, cd_false

# ======================================================
# BAIXAR RELATORIO
# ======================================================

def baixar_relatorio_grupo(session, grupo, params, cd_true, cd_false):

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": RELATORIO_URL,
        "Origin": "https://prodwin.ebba.com.br",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",

        "__VIEWSTATE": params["__VIEWSTATE"],
        "__VIEWSTATEGENERATOR": params["__VIEWSTATEGENERATOR"],
        "__EVENTVALIDATION": params["__EVENTVALIDATION"],

        "ctl00$cphMain$ddlGrupoMaquina": str(grupo),
        "ctl00$cphMain$ddlMaquina": "0",

        "ctl00$cphMain$txtDtInicio": DATA_RELATORIO_SITE,
        "ctl00$cphMain$txtDtFim": DATA_RELATORIO_SITE,

        "ctl00$cphMain$ddlTurno": "0",
        "ctl00$cphMain$cbTipo": "0",
        "ctl00$cphMain$ddlAreaResponsavel": "0",

        "ctl00$cphMain$txtSearch": "",

        # 🔥 dinâmico (extraído do HTML)
        "cdParada_True": cd_true,
        "cdParada_False": cd_false,

        "ctl00$cphMain$btnSalvar": "Exportar"
    }

    if params["__EVENTVALIDATION"]:
        payload["__EVENTVALIDATION"] = params["__EVENTVALIDATION"]

    r = session.post(
        RELATORIO_URL,
        headers=headers,
        data=payload
    )

    # 🔥 DETECÇÃO DE VIEWSTATE EXPIRADO
    if b"<html" in r.content[:200].lower():

        registrar_log(f"Grupo {grupo}: VIEWSTATE expirado ou sessão inválida. Recarregando...")

        # 🔁 recarrega parâmetros
        params_novo = obter_params_relatorio(session)

        payload["__VIEWSTATE"] = params_novo["__VIEWSTATE"]
        payload["__VIEWSTATEGENERATOR"] = params_novo["__VIEWSTATEGENERATOR"]
        payload["__EVENTVALIDATION"] = params_novo["__EVENTVALIDATION"]

        # 🔁 tenta novamente
        r = session.post(RELATORIO_URL, headers=headers, data=payload)

        # ❌ se ainda falhar
        if b"<html" in r.content[:200].lower():
            registrar_log(f"Grupo {grupo}: Falhou mesmo após recarregar VIEWSTATE")
            return b""  

    registrar_log(f"Tamanho arquivo grupo {grupo}: {len(r.content)} bytes")

    return r.content

# ======================================================
# PROCESSAR XLSX
# ======================================================

def processar_xlsx(xlsx):

    try:
        df_raw = pd.read_excel(BytesIO(xlsx), header=None)

        unidade = None

        # 🔍 1. Capturar "Grupo de Máquina"
        for i in range(len(df_raw)):
            if str(df_raw.iloc[i, 0]).strip() == "Grupo de Máquina":
                unidade = df_raw.iloc[i, 2]  # valor está na coluna 2
                break

        # 🔍 2. Encontrar linha do cabeçalho real
        header_row = None

        for i in range(len(df_raw)):
            linha = df_raw.iloc[i].astype(str).str.strip().tolist()

            if "Máquina" in linha and "Inicio" in linha and "Fim" in linha:
                header_row = i
                break

        if header_row is None:
            registrar_log("Cabeçalho não encontrado no XLSX")
            return pd.DataFrame()

        # 📊 3. Ler dados com cabeçalho correto
        df = pd.read_excel(BytesIO(xlsx), header=header_row)

        # 🧹 4. Limpeza básica
        df.columns = df.columns.astype(str).str.strip()
        df = df.dropna(axis=1, how="all")

        df["Motivo Parada"] = (
            df["Motivo Parada"]
            .astype(str)
            .str.replace(r"^[^\w]+\s*", "", regex=True)
            .str.strip()
        )

        # 🔥 5. Adicionar Unidade
        df["Unidade"] = unidade

        # 🧹 6. Remover linhas inválidas
        if "Inicio" not in df.columns:
            registrar_log(f"Colunas encontradas: {df.columns.tolist()}")
            return pd.DataFrame()

        df = df.dropna(subset=["Inicio"])

        # 🔄 7. Conversões de tipo (mantendo nomes originais)
        df["Inicio"] = pd.to_datetime(df["Inicio"], errors="coerce")
        df["Fim"] = pd.to_datetime(df["Fim"], errors="coerce")

        if "Duração" in df.columns:
            df["Duração"] = pd.to_timedelta(df["Duração"], errors="coerce")

        if "Tempo sem peso" in df.columns:
            df["Tempo sem peso"] = pd.to_timedelta(df["Tempo sem peso"], errors="coerce")

        if "Tempo com peso" in df.columns:
            df["Tempo com peso"] = pd.to_timedelta(df["Tempo com peso"], errors="coerce")

        # 📈 8. Ordenação
        df = df.sort_values("Inicio")

        return df.reset_index(drop=True)

    except Exception as e:
        registrar_log(f"Erro processando XLSX: {e}")
        return pd.DataFrame()

# ======================================================
# HISTORICO DUCKDB
# ======================================================

def salvar_paradas_duckdb(df):

    if df.empty:
        return

    # 🧠 1. pegar apenas a última linha de cada máquina
    df_ultimas = (
        df.sort_values("Inicio")
          .groupby("Máquina")
          .tail(1)
    )

    con = duckdb.connect(DB_CONSULTA, read_only=False)

    # 🧱 2. tabela com nomes ORIGINAIS + Unidade
    con.execute("""
    CREATE TABLE IF NOT EXISTS paradas_historico(
        "Máquina" VARCHAR,
        "OP" VARCHAR,
        "Produto" VARCHAR,
        "Parada" VARCHAR,
        "Motivo Parada" VARCHAR,
        "Turno" VARCHAR,
        "Inicio" TIMESTAMP,
        "Fim" TIMESTAMP,
        "Duração" INTERVAL,
        "Tempo sem peso" INTERVAL,
        "Tempo com peso" INTERVAL,
        "Unidade" VARCHAR
    )
    """)

    con.register("temp", df_ultimas)

    # 🚫 3. deduplicação por Máquina + Inicio
    con.execute("""
    INSERT INTO paradas_historico
    SELECT
        t."Máquina",
        t."OP",
        t."Produto",
        t."Parada",
        t."Motivo Parada",
        t."Turno",
        t."Inicio",
        t."Fim",
        t."Duração",
        t."Tempo sem peso",
        t."Tempo com peso",
        t."Unidade"
    FROM temp t
    LEFT JOIN paradas_historico p
        ON p."Máquina" = t."Máquina"
        AND p."Inicio" = t."Inicio"
    WHERE p."Máquina" IS NULL
    """)
    con.close()

# ======================================================
# BASE CONSULTA
# ======================================================

def atualizar_paradas_consulta(df):

    if df.empty:
        return

    con = duckdb.connect(DB_CONSULTA, read_only=False)

    con.execute("""
    CREATE TABLE IF NOT EXISTS paradas_consulta(
        "Máquina" VARCHAR,
        "OP" VARCHAR,
        "Produto" VARCHAR,
        "Parada" VARCHAR,
        "Motivo Parada" VARCHAR,
        "Turno" VARCHAR,
        "Inicio" TIMESTAMP,
        "Fim" TIMESTAMP,
        "Duração" INTERVAL,
        "Tempo sem peso" INTERVAL,
        "Tempo com peso" INTERVAL,
        "Unidade" VARCHAR,
        "DataCarga" TIMESTAMP
    )
    """)

    # 🧠 último registro por máquina
    df_final = (
        df.sort_values("Inicio")
          .groupby("Máquina")
          .tail(1)
          .copy()
    )

    df_final["DataCarga"] = datetime.now()

    con.register("temp", df_final)

    # 🚫 deduplicação
    con.execute("""
    INSERT INTO paradas_consulta
    SELECT
        t."Máquina",
        t."OP",
        t."Produto",
        t."Parada",
        t."Motivo Parada",
        t."Turno",
        t."Inicio",
        t."Fim",
        t."Duração",
        t."Tempo sem peso",
        t."Tempo com peso",
        t."Unidade",
        t."DataCarga"
    FROM temp t
    LEFT JOIN paradas_consulta p
        ON p."Máquina" = t."Máquina"
        AND p."Inicio" = t."Inicio"
    WHERE p."Máquina" IS NULL
    """)

    # 🧹 manter apenas últimos 2 dias
    con.execute("""
        DELETE FROM paradas_consulta
        WHERE "Inicio" < (
            SELECT MAX("Inicio") - INTERVAL 2 DAY
            FROM paradas_consulta
        )
    """)

    con.close()

# ======================================================
# EXECUÇÃO DO ETL
# ======================================================

def executar_etl_paradas():

    registrar_log("ETL das paradas iniciado")

    session = requests.Session()

    login(session)

    limpar_xlsx_antigos()

    # GET apenas uma vez
    params = obter_params_relatorio(session)

    lista_dfs = []

    for grupo in [1, 2, 3]:

        registrar_log(f"Baixando grupo {grupo}")

        params = obter_params_relatorio(session)
        cd_true, cd_false = extrair_cd_paradas(session)

        xlsx = None

        try:
            #params = obter_params_relatorio(session)

            xlsx = baixar_relatorio_grupo(session, grupo, params, cd_true, cd_false)

            if not xlsx:

                registrar_log(f"Grupo {grupo} retornou vazio")
                continue

            salvar_xlsx_bruto(xlsx, grupo)

            df = processar_xlsx(xlsx)

            if not df.empty:

                lista_dfs.append(df)

                registrar_log(f"{len(df)} registros grupo {grupo}")

            else:

                registrar_log(f"Grupo {grupo} sem registros")

        except Exception as e:

            registrar_log(f"Erro grupo {grupo}: {e}")

        time.sleep(12)

    if not lista_dfs:

        registrar_log("Nenhum dado retornado")
        return

    df_final = pd.concat(lista_dfs, ignore_index=True)

    registrar_log(f"Total registros: {len(df_final)}")

    salvar_paradas_duckdb(df_final)

    df_consulta = (
        df_final
        .sort_values("Inicio")
        .groupby("Máquina")
        .tail(1)
    )

    atualizar_paradas_consulta(df_consulta)

    registrar_log("ETL ETL das paradas finalizado")