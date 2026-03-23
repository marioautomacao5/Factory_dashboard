# ======================================================
# ARQUIVO CORRETO
# ======================================================

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
from datetime import datetime
import duckdb
import re  # ✅ NOVO

# ======================================================
# CONFIGURAÇÕES
# ======================================================

usuario = "dash.producao"
senha = "Ebba@123456789"

LOGIN_URL = "https://prodwin.ebba.com.br/Usuario.Login.aspx?cmd=logout"
RELATORIO_URL = "https://prodwin.ebba.com.br/report/default/producao/RelatorioProducaoHora.aspx"

MAQUINAS = ["9","6","10","22","5","1","2","3","18","12","17","16","20","21"]

TURNO = "0"

DATA_RELATORIO_SITE = datetime.now().strftime("%d/%m/%Y")
DATA_RELATORIO_BANCO = datetime.now().strftime("%Y-%m-%d")

# ======================================================
# ESTRUTURA DE PASTAS
# ======================================================

BASE_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_RAW = os.path.join(BASE_PROJETO, "data", "raw", "relatorios")
DATA_HTML = os.path.join(BASE_PROJETO, "data", "raw", "html")
DATA_WAREHOUSE = os.path.join(BASE_PROJETO, "data", "warehouse")

LOG_DIR = os.path.join(BASE_PROJETO, "logs")

ARQ_LOG = os.path.join(LOG_DIR, "pipeline.log")
ARQ_PRODUCAO = os.path.join(DATA_RAW, "prodwin_producao.csv")

DB_CONSULTA = os.path.join(DATA_WAREHOUSE, "producao.duckdb")

os.makedirs(DATA_RAW, exist_ok=True)
os.makedirs(DATA_HTML, exist_ok=True)
os.makedirs(DATA_WAREHOUSE, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# ======================================================
# UTILITÁRIOS
# ======================================================

def parse_int(valor):
    if valor is None:
        return None
    
    valor = (
        valor.replace(".", "")
             .replace(",", "")
             .strip()
    )
    
    return pd.to_numeric(valor, errors="coerce")

import pandas as pd

def parse_float(valor):
    """
    Converte string ou número para float, tratando pontos como milhares e vírgula como decimal.
    """
    if valor is None or pd.isna(valor):
        return None
    
    # Se já for numérico, retorna como float
    if isinstance(valor, (int, float)):
        return float(valor)
    
    # remove espaços
    valor = valor.strip()
    
    # substitui separador de milhares (ponto) e coloca ponto como decimal
    valor = valor.replace(".", "").replace(",", ".")
    
    # converte para float
    return pd.to_numeric(valor, errors="coerce")

# ======================================================
# 🆕 NOVO - CÁLCULO CX
# ======================================================

def calcular_producao_cx(formato, producao_bruta):

    if formato is None or pd.isna(producao_bruta):
        return None

    formato = formato.upper()

    try:
        if formato.startswith("27"):
            return producao_bruta / 27

        if formato == "12X1000":
            return producao_bruta / 12

        if formato == "12X500":
            return producao_bruta / 12

        if formato in ["6X900", "6X950", "6X1000", "6X1350", "6X275"]:
            return producao_bruta / 6

    except:
        return None

    return None


def calcular_perda_ritmo(ciclo_padrao, ciclo_medido, producao):

    ciclo_padrao = parse_float(ciclo_padrao)
    ciclo_medido = parse_float(ciclo_medido)
    producao = parse_float(producao)

    #registrar_log(f"Parâmetros enviados tratados {ciclo_padrao}, {ciclo_medido}, {producao}")

    # validações
    if any(pd.isna(x) for x in [ciclo_padrao, ciclo_medido, producao]):
       return None

    try:

        if ciclo_medido <= 0:
            tempo_prod = 0

        else:
            # tempo produtivo (segundos)
            tempo_por_peca_medido = ciclo_medido / 1000
            pecas_por_segundo = 1/tempo_por_peca_medido

            tempo_prod = producao/pecas_por_segundo # Em segundos

        # tempo por peça (segundos)
        tempo_por_peca = ciclo_padrao / 1000

        # tempo ideal para produzir o que foi produzido
        tempo_ideal = producao * tempo_por_peca 

        # perda de ritmo (tempo perdido)
        perda_tempo =  tempo_prod - tempo_ideal

        #registrar_log(f"Perda de ritmo {perda_tempo}")

        # evitar valores negativos
        return max(0, perda_tempo)

    except Exception:
        registrar_log(f"Erro na função de calculo perda de ritmo está sendo acionado. Parâmetros enviados {ciclo_padrao}, {ciclo_medido}, {producao}")
        return None

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
# LIMPEZA HTML
# ======================================================

def limpar_htmls_antigos(dias=15):
    limite = time.time() - (dias * 86400)

    for arq in os.listdir(DATA_HTML):
        caminho = os.path.join(DATA_HTML, arq)
        if os.path.getmtime(caminho) < limite:
            os.remove(caminho)

# ======================================================
# SALVAR HTML
# ======================================================

def salvar_html_bruto(html, maquina):
    nome = f"maq_{maquina}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    caminho = os.path.join(DATA_HTML, nome)

    with open(caminho, "wb") as f:
        f.write(html)

# ======================================================
# LOGIN
# ======================================================

def login(session):
    headers = {"User-Agent":"Mozilla/5.0"}

    r = session.get(LOGIN_URL,headers=headers)
    soup = BeautifulSoup(r.text,"html.parser")

    viewstate = soup.find("input",{"name":"__VIEWSTATE"})["value"]
    viewstategenerator = soup.find("input",{"name":"__VIEWSTATEGENERATOR"})["value"]

    payload = {
        "__VIEWSTATE":viewstate,
        "__VIEWSTATEGENERATOR":viewstategenerator,
        "txtUsuario":usuario,
        "txtSenha":senha,
        "cbLanguage":"1",
        "Button1":"OK"
    }

    session.post(LOGIN_URL,headers=headers,data=payload)

# ======================================================
# BAIXAR RELATORIO
# ======================================================

def baixar_relatorio(session,maquina):

    headers={"User-Agent":"Mozilla/5.0"}

    r = session.get(RELATORIO_URL,headers=headers)
    soup = BeautifulSoup(r.text,"html.parser")

    viewstate = soup.find("input",{"name":"__VIEWSTATE"})["value"]
    viewstategenerator = soup.find("input",{"name":"__VIEWSTATEGENERATOR"})
    viewstategenerator = viewstategenerator["value"] if viewstategenerator else ""

    payload = {
        "__VIEWSTATE":viewstate,
        "__VIEWSTATEGENERATOR":viewstategenerator,
        "ctl00$cphMain$cbMaquina":maquina,
        "ctl00$cphMain$cbTurno":TURNO,
        "ctl00$cphMain$txtDia":DATA_RELATORIO_SITE,
        "ctl00$cphMain$btnSalvar":"Exportar"
    }

    r = session.post(RELATORIO_URL,headers=headers,data=payload)

    return r.content

# ======================================================
# PROCESSAR HTML
# ======================================================

#Função antiga

def processar_html(html, maquina_id):

    soup = BeautifulSoup(html, "html.parser")
    
    tag_x93 = soup.find("td", class_="x93")
    if tag_x93:
        nome_linha = tag_x93.get_text(strip=True)
    else:
        nome_linha = f"MAQ_{maquina_id}"
    # ----------------------------------------------------------

    tabelas = soup.find_all("table")

    # 1. PEGAR TODAS AS TABELAS (Sem pular as 4 primeiras fixas por enquanto)
    for tab in tabelas:
        if not tab.find("td", class_="x01"):
            continue

    registrar_log(f"DEBUG: {len(tabelas)} tabelas encontradas no total.")

    dados = []

    for tab in tabelas:
        # Procuramos a célula de período (x01). 
        td_hora = tab.find("td", class_="x01")
        
        if not td_hora:
            continue
            
        # Pega a linha onde a hora foi encontrada
        tr = td_hora.parent
        tds = tr.find_all("td", recursive=False)

        # Se a linha tem poucas colunas, não é o que queremos
        if len(tds) < 6:
            continue

        try:
            # --- EXTRAÇÃO ---
            hora_texto = tds[0].get_text(strip=True)

            hora_inicial = None
            hora_final = None

            if " - " in hora_texto:
                partes = hora_texto.split(" - ", 1)
                hora_inicial = partes[0].strip()
                hora_final = partes[1].strip()
            else:
                hora_inicial = hora_texto.strip()
                hora_final = None

            oee_txt = tds[1].get_text(strip=True)
            oee = pd.to_numeric(
                oee_txt.replace("%", "").replace(",", ".").strip(),
                errors="coerce"
            )

            produto = ""
            formato = None
            producao_bruta_cx = None

            ciclo_padrao = None
            ciclo_medio = None
            meta_hora_sistema = None
            producao_bruta = None
            
            # Sub-tabela Produto (geralmente a 5ª célula)
            produto_tab = tds[4].find("table")

            if produto_tab:
                tds_prod = produto_tab.find_all("td")

                if len(tds_prod) >= 6:

                    produto = tds_prod[0].get_text(strip=True)

                    regex_formato = r"\b(?:6[xX](?:1|275|900|950|1000|1350)|12[xX](?:1|500|1000)|27[xX](?:150|180|200))(?!\d)"

                    # ✅ NOVO
                    match = re.search(regex_formato, produto)
                    if match:
                        formato = match.group(0).upper()

                    ciclo_padrao = pd.to_numeric(
                        tds_prod[1].get_text(strip=True)
                            .replace(".", "")
                            .replace(",", "."),
                        errors="coerce"
                    )

                    ciclo_medio = pd.to_numeric(
                        tds_prod[2].get_text(strip=True)
                            .replace(".", "")
                            .replace(",", "."),
                        errors="coerce"
                    )

                    meta_hora_sistema = parse_int(tds_prod[3].get_text(strip=True))
                    producao_bruta = parse_int(tds_prod[4].get_text(strip=True))

                    # ✅ NOVO
                    producao_bruta_cx = calcular_producao_cx(formato, producao_bruta)

            # Sub-tabelas Paradas (geralmente a 6ª célula)
            sub_tabs = tds[5].find_all("table")
            paradas_texto = []
            tempo_total = "00:00:00"
            
            for ptab in sub_tabs:
                p_tds = ptab.find_all("td")
                if not p_tds: continue
                desc = p_tds[0].get_text(strip=True)
                if desc.lower() == "total":
                    if len(p_tds) > 1:
                        tempo_total = p_tds[1].get_text(strip=True)
                        tempo_total = tempo_total.split(".")[0]
                else:
                    paradas_texto.append(desc)

            dados.append({
                "Dia": DATA_RELATORIO_BANCO,
                "LinhaProducao": nome_linha,
                "HoraInicial": hora_inicial,
                "HoraFinal": hora_final,
                "OEE": oee,
                "Produto": produto,
                "Formato": formato,
                "CicloPadrao": ciclo_padrao,
                "CicloMedio": ciclo_medio,
                "MetaHoraSistema": meta_hora_sistema,
                "ProducaoBruta": producao_bruta,
                "ProducaoBrutaCx": producao_bruta_cx,
                "Paradas": " | ".join(paradas_texto),
                "TempoTotalParada": tempo_total,
                "PerdaRitmo": None
            })

        except Exception as e:
            registrar_log(f"⚠️ Erro ao processar tabela {e}")

    df = pd.DataFrame(dados)

    # ----------------------------------------------------------

    # TRECHO CRÍTICO 

    #registrar_log(f"HoraInicio: {df["HoraInicial"]}")
    df["HoraInicial"] = pd.to_datetime(df["HoraInicial"], format="%H:%M", errors="coerce").dt.strftime("%H:%M:%S")
    #registrar_log(f"HoraInicio: {df["HoraInicial"]}")
    df["HoraFinal"] = pd.to_datetime(df["HoraFinal"], format="%H:%M", errors="coerce").dt.strftime("%H:%M:%S")
    #registrar_log(f"HoraFinal: {df["HoraFinal"]}")

    df["MetaHoraSistema"] = df["MetaHoraSistema"].astype("Int64")
    df["ProducaoBruta"] = df["ProducaoBruta"].astype("Int64")

    df["TempoTotalParada"] = pd.to_timedelta(df["TempoTotalParada"], errors="coerce")

    df["PerdaRitmo"] = pd.to_timedelta(df["PerdaRitmo"], unit="s")

    #df["TempoTotalParada_segundos"] = pd.to_timedelta(df["TempoTotalParada"]).dt.total_seconds()
    #df["timestamp"] = pd.to_datetime(df["Dia"]) + pd.to_timedelta(df["HoraInicial"].astype(str))
    #df["Hora"] = pd.to_datetime(df["HoraInicial"], format="%H:%M:%S").dt.hour

    # ----------------------------------------------------------
    df["PerdaRitmo"] = df.apply(
        lambda row: calcular_perda_ritmo(
            row["CicloPadrao"],
            row["CicloMedio"],
            row["ProducaoBruta"]
        ),
        axis=1
    )

    df["PerdaRitmo"] = pd.to_numeric(df["PerdaRitmo"], errors="coerce")

    return df

# ======================================================
# CONSULTA
# ======================================================

def atualizar_base_consulta(df):

    if df.empty:
        return

    con = duckdb.connect(DB_CONSULTA, read_only=False)

    # ======================================================
    # 🔹 GARANTE TABELA
    # ======================================================
    con.execute("""
    CREATE TABLE IF NOT EXISTS producao_consulta(
        Dia DATE,
        LinhaProducao VARCHAR,
        HoraInicial TIME,
        HoraFinal TIME,
        OEE DOUBLE,
        Produto VARCHAR,
        Formato VARCHAR,
        CicloPadrao DOUBLE,
        CicloMedio DOUBLE,
        MetaHoraSistema BIGINT,
        ProducaoBruta BIGINT,
        ProducaoBrutaCx DOUBLE,
        Paradas VARCHAR,
        TempoTotalParada VARCHAR,
        PerdaRitmo DOUBLE,
        DataCarga TIMESTAMP
    )
    """)

    # ======================================================
    # 🔹 CONTROLE DE DUPLICIDADE
    # ======================================================
    existentes = con.execute("""
        SELECT Dia, LinhaProducao, HoraFinal FROM producao_consulta
    """).df()

    df["_chave"] = (
        df["Dia"].astype(str) + "|" +
        df["LinhaProducao"] + "|" +
        df["HoraFinal"].astype(str)
    )

    existentes["_chave"] = (
        existentes["Dia"].astype(str) + "|" +
        existentes["LinhaProducao"] + "|" +
        existentes["HoraFinal"].astype(str)
    )

    df = df[~df["_chave"].isin(existentes["_chave"])].copy()

    if df.empty:
        con.close()
        return

    # ======================================================
    # 🔹 DATA DE CARGA
    # ======================================================
    df["DataCarga"] = datetime.now()

    # Remove coluna auxiliar
    df = df.drop(columns=["_chave"])

    con.register("temp", df)

    con.execute("""
    INSERT INTO producao_consulta
    SELECT * FROM temp
    """)

    # ======================================================
    # 🔹 LIMPEZA (mantém últimos 2 dias)
    # ======================================================
    con.execute("""
        DELETE FROM producao_consulta
        WHERE Dia < (
            SELECT MAX(Dia) - INTERVAL 2 DAY FROM producao_consulta
        )
    """)

    con.close()

# ======================================================
# HISTORICO
# ======================================================

def salvar_historico_duckdb(df):

    if df.empty:
        return

    con = duckdb.connect(DB_CONSULTA, read_only=False)

    con.execute("""
    CREATE TABLE IF NOT EXISTS producao_historico(
        Dia DATE,
        LinhaProducao VARCHAR,
        HoraInicial TIME,
        HoraFinal TIME,
        OEE DOUBLE,
        Produto VARCHAR,
        Formato VARCHAR,
        CicloPadrao DOUBLE,
        CicloMedio DOUBLE,
        MetaHoraSistema BIGINT,
        ProducaoBruta BIGINT,
        ProducaoBrutaCx DOUBLE,
        Paradas VARCHAR,
        PerdaRitmo DOUBLE,
        TempoTotalParada VARCHAR
    )
    """)

    existentes = con.execute("""
        SELECT Dia,LinhaProducao,HoraFinal FROM producao_historico
    """).df()

    df["_chave"] = (
        df["Dia"].astype(str) + "|" +
        df["LinhaProducao"] + "|" +
        df["HoraFinal"].astype(str)
    )

    existentes["_chave"] = (
        existentes["Dia"].astype(str) + "|" +
        existentes["LinhaProducao"] + "|" +
        existentes["HoraFinal"].astype(str)
    )

    df = df[~df["_chave"].isin(existentes["_chave"])]

    if not df.empty:
        con.register("temp", df)

        con.execute("""
        INSERT INTO producao_historico
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
            PerdaRitmo,
            TempoTotalParada
        FROM temp
        """)

        registrar_log(f"{len(df)} linhas inseridas no histórico")

    con.close()

# ======================================================
# 🔥 EXECUÇÃO (NÃO FOI ALTERADA)
# ======================================================

def executar_etl():

    registrar_log("ETL de produção iniciado")

    session = requests.Session()
    login(session)

    lista_dfs = []
    lista_ultimas = []

    limpar_htmls_antigos()

    for maquina in MAQUINAS:

        registrar_log(f"Baixando máquina {maquina}")

        html = baixar_relatorio(session, maquina)
        salvar_html_bruto(html, maquina)

        df = processar_html(html, maquina)

        if not df.empty:
            lista_dfs.append(df)
            lista_ultimas.append(df.tail(1))

        time.sleep(0.5)

    if lista_dfs:

        df_final = pd.concat(lista_dfs, ignore_index=True)

        salvar_historico_duckdb(df_final)

    if lista_ultimas:

        df_consulta = pd.concat(lista_ultimas, ignore_index=True)

        atualizar_base_consulta(df_consulta)

    registrar_log("ETL de produção finalizado")