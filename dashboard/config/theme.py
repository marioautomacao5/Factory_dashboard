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

        /* DESTAQUE DAS LEGENDAS (Labels de todas as colunas) */
        /* Usamos seletores múltiplos para garantir que nada sobrescreva o branco */
        [data-testid="stMetricLabel"] p, 
        [data-testid="stMetricLabel"] > div > p,
        [data-testid="stMetricLabel"] label {
            color: #ffffff !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            opacity: 1 !important; /* Resolve o problema de parecer 'apagado' */
            margin-bottom: 5px;
        }

        /* DESTAQUE DO VALOR (Número de todas as colunas) */
        [data-testid="stMetricValue"] div,
        [data-testid="stMetricValue"] > div {
            color: #ffffff !important;
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            opacity: 1 !important;
        }

        /* --- CARDS DOS GRÁFICOS --- */
        /* Estiliza o contêiner border=True para parecer um card industrial */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #1b1f2a !important;
            border: 1px solid #2d323e !important;
            border-radius: 12px !important;
            padding: 15px !important;
            margin-bottom: 20px !important;
        }

        /* Ajuste de títulos e divisores */
        h1, h2, h3, h4 { color: white !important; font-weight: 700 !important; }
        hr { border-top: 1px solid #2d323e !important; }
        
        </style>
        """,
        unsafe_allow_html=True
    )

    # 2. Configuração Global do Plotly
    pio.templates.default = "plotly_dark"
    pio.templates["plotly_dark"].layout.paper_bgcolor = 'rgba(0,0,0,0)'
    pio.templates["plotly_dark"].layout.plot_bgcolor = 'rgba(0,0,0,0)'
    pio.templates["plotly_dark"].layout.font.color = 'white'
    pio.templates["plotly_dark"].layout.margin = dict(t=80, b=40, l=40, r=40)