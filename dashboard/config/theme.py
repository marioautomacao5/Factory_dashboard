import streamlit as st
import plotly.io as pio

def aplicar_tema():
    # 1. Configuração do CSS para a interface do Streamlit
    st.markdown(
        """
        <style>
        /* Fundo principal do App */
        .stApp {
            background-color: #0e1117;
            color: white;
        }

        /* --- CARDS DE MÉTRICA (TOPO) --- */
        div[data-testid="stMetric"] {
            background-color: #1b1f2a;
            padding: 20px 25px;
            border-radius: 12px;
            border: 1px solid #2d323e;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
        }

        /* DESTAQUE DA LEGENDA (Texto Superior) */
        div[data-testid="stMetricLabel"] > div > p {
            color: #ffffff !important; /* Branco puro para destaque total */
            font-size: 1.15rem !important; /* Aumentado levemente */
            font-weight: 700 !important; /* Negrito extra */
            text-transform: uppercase;
            letter-spacing: 1.5px; /* Mais espaçamento para leitura industrial */
            margin-bottom: 5px;
        }

        /* DESTAQUE DO VALOR (Número) */
        div[data-testid="stMetricValue"] > div {
            color: #ffffff !important;
            font-size: 2.5rem !important; /* Aumentado para impacto */
            font-weight: 800 !important;
        }

        /* --- CARDS DOS GRÁFICOS --- */
        /* Alvo: Contêineres que possuem borda (st.container(border=True)) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #1b1f2a !important;
            border: 1px solid #2d323e !important;
            border-radius: 12px !important;
            padding: 10px !important;
            margin-bottom: 15px !important;
        }

        /* Títulos do Dashboard */
        h1, h2, h3, h4 {
            color: white !important;
            font-weight: 700 !important;
        }

        /* Remove linhas extras de divisores dentro de cards se necessário */
        hr {
            margin: 1em 0 !important;
            border-top: 1px solid #2d323e !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 2. Configuração Global do Plotly
    # Definimos como 'plotly_dark' e forçamos transparência total 
    # para que o gráfico herde o fundo #1b1f2a dos nossos cards.
    pio.templates.default = "plotly_dark"
    pio.templates["plotly_dark"].layout.paper_bgcolor = 'rgba(0,0,0,0)'
    pio.templates["plotly_dark"].layout.plot_bgcolor = 'rgba(0,0,0,0)'
    pio.templates["plotly_dark"].layout.font.color = 'white'