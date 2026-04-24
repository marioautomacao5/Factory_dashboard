from pathlib import Path
import duckdb
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[3]
DB_PATH = BASE_DIR / "data" / "warehouse" / "producao.duckdb"


def _carregar_unidades():
    if not DB_PATH.exists():
        return []
    try:
        con = duckdb.connect(str(DB_PATH), read_only=True)
        tabelas = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
        if "paradas_consulta" not in tabelas:
            con.close()
            return []
        rows = con.execute("""
            SELECT DISTINCT "Unidade"
            FROM paradas_consulta
            WHERE "Unidade" IS NOT NULL
            ORDER BY "Unidade"
        """).fetchall()
        con.close()
        return [r[0].strip().upper() for r in rows if r[0]]
    except Exception:
        return []


def exibir_seletor_unidade():
    """
    Renderiza a tela de seleção de unidade fabril.
    Bloqueia o restante do app até que o usuário selecione uma unidade.
    Armazena a escolha em st.session_state["unidade_rls"].
    """
    if st.session_state.get("unidade_rls"):
        return

    st.markdown(
        """
        <style>
        .rls-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff;
            text-align: center;
            margin-bottom: 0.3rem;
        }
        .rls-sub {
            font-size: 1rem;
            color: #8b949e;
            text-align: center;
            margin-bottom: 2.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown('<p class="rls-title">🏭 Packaging View</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="rls-sub">Selecione a unidade fabril para acessar o dashboard</p>',
            unsafe_allow_html=True,
        )

        unidades = _carregar_unidades()

        if not unidades:
            st.warning("Nenhuma unidade encontrada no banco de dados. Verifique o ETL.")
            st.stop()

        with st.form("form_rls_unidade"):
            unidade = st.selectbox(
                "Unidade fabril",
                options=unidades,
                index=0,
                label_visibility="collapsed",
                placeholder="Selecione...",
            )
            submitted = st.form_submit_button(
                "Entrar →",
                use_container_width=True,
                type="primary",
            )

        if submitted and unidade:
            st.session_state["unidade_rls"] = unidade
            st.rerun()

    st.stop()
