import sys
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

import none as st
from streamlit_autorefresh import st_autorefresh

from dashboard.config.theme import aplicar_tema
from dashboard.data.loader import carregar_dados, carregar_paradas, carregar_metas, aplicar_metas
from dashboard.services.transforms import preparar_dados
from dashboard.services.metrics import calcular_metricas

from dashboard.charts.gauge import gauge_oee
from dashboard.charts.line_oee import linha_oee
from dashboard.charts.line_ritmo import linha_ritmo_global, linha_ritmo_soma, linha_ritmo_media
from dashboard.charts.oee_rosquinha_por_turno import rosquinha_turnos
from dashboard.charts.pareto_paradas_turno import pareto_paradas_turno

from dashboard.ui.filters import aplicar_filtros


# ======================================================
# PAGE SETUP
# ======================================================

st.set_page_config(
    page_title="Packging view",
    layout="wide"
)

aplicar_tema()

st_autorefresh(interval=60000)

# ======================================================
# HEADER
# ======================================================

st.title("🏭 Packging view dashboard")
# st.caption("Refresh each minute")
st.divider()

# ======================================================
# LOADERS
# ======================================================

@st.cache_data(ttl=60)
def load_producao():
    df = carregar_dados()

    if df.empty:
        return df

    df = preparar_dados(df)

    if "LinhaProducao" not in df.columns:
        return pd.DataFrame()

    df["LinhaProducao"] = (
        df["LinhaProducao"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df

def formatar_duracao(segundos):
    if pd.isna(segundos):
        return "00:00:00"
    segundos = int(segundos)
    h = segundos // 3600
    m = (segundos % 3600) // 60
    s = segundos % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


@st.cache_data(ttl=60)
def load_paradas():
    df = carregar_paradas()

    if df.empty:
        return df

    if "Máquina" not in df.columns:
        return pd.DataFrame()

    df["Máquina"] = pd.to_numeric(df["Máquina"], errors="coerce")

    return df


# ======================================================
# LOADING
# ======================================================

df = load_producao()
df_paradas = load_paradas()

df_metas = carregar_metas()
df = aplicar_metas(df)

if df.empty:
    st.warning(" No data available. See ETL loop.")
    st.stop()

# ======================================================
# FILTERS
# ======================================================

df, df_paradas = aplicar_filtros(df, df_paradas)

# ======================================================
# METRICS
# ======================================================

metricas = calcular_metricas(df)

col1, col2, col3, col4 = st.columns(4)

col1.metric("OEE shift atual", f"{metricas.get('oee_turno', 0):.2f}%")

col2.metric(
    label="OEE Target",
    value=f"{metricas.get('meta_oee_filtrada', 0):.2f}%"
)

col3.metric(
    "Production (Cases)",
    f"{int(metricas.get('producao_total_turnoCx', 0)):,}".replace(",", ".")
)

col4.metric(
    "Shift Speed loss",
    formatar_duracao(metricas.get("perda_total_turno", 0))
)

st.divider()

# ======================================================
# GRAPHICS
# ======================================================

col1, col2 = st.columns([1, 2])

with col1:
    sub = st.container()
    with sub:
        st.plotly_chart(
            gauge_oee(
                valor=metricas.get("oee_turno", 0),
                meta_oee=metricas.get("meta_oee_filtrada", 85)
            ),
            width="stretch", 
            theme="none"
        )
        st.plotly_chart(
            rosquinha_turnos(df),
            width="stretch",
            theme="none"
        )


with col2:
    sub = st.container()
    with sub:
        st.plotly_chart(
            linha_oee(
                df=metricas.get("df_1h", pd.DataFrame()),
                meta_oee=metricas.get("meta_oee_filtrada", 85)
            ),
            width='stretch',
            theme="none"
        )
        st.plotly_chart(
            pareto_paradas_turno(df_paradas),
            width="stretch",
            theme="none"
        )

st.divider()

st.plotly_chart(
            linha_ritmo_global(metricas.get("Velocidade_nominal_individual")),
            width="stretch",
            key="Velocidade_individual",
            theme="none"
        )

st.divider()

st.plotly_chart(
            linha_ritmo_soma(metricas.get("velocidade_medida_global_soma")),
            width="stretch",
            key="Velocidade_agragada_por_soma",
            theme="none"
        )

st.divider()

st.plotly_chart(
            linha_ritmo_media(metricas.get("velocidade_medida_global_media")),
            width="stretch",
            key="Velocidade_agregada_por_media",
            theme="none"
        )