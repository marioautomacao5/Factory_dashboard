import streamlit as st
import plotly.io as pio

def aplicar_tema():
    # 1. Configuração do CSS para a interface do Streamlit
    st.markdown(
        """
        <style>
        /* Fundo principal */
        .stApp {
            background-color: #0e1117;
            color: white;
        }

        /* Estilização dos Cards de Métrica */
        div[data-testid="stMetric"] {
            background-color: #1b1f2a;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #2d323e;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        /* Estilo para o contêiner dos gráficos (simulando um card) */
        .chart-card {
            background-color: #1b1f2a;
            border: 1px solid #2d323e;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 20px;
        }

        /* Estilo para transformar contêineres específicos em cards */
        div[data-testid="stVerticalBlockBorderWrapper"] > div > div > div[data-testid="stVerticalBlock"] > div.element-container:has(iframe) {
            background-color: #1b1f2a;
            border: 1px solid #2d323e;
            border-radius: 12px;
            padding: 15px;
        }
        
        /* Destaque do Valor da Métrica (Número) */
        div[data-testid="stMetricValue"] > div {
            color: #ffffff !important;
            font-size: 2.2rem !important;
            font-weight: 700 !important;
        }

        /* Destaque do Rótulo da Métrica (Texto Superior) */
        div[data-testid="stMetricLabel"] > div > p {
            color: #9da5b4 !important;
            font-size: 1.1rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Ajuste de cor do label da métrica */
        div[data-testid="stMetricLabel"] > div {
            color: #9da5b4 !important;
        }

        /* Títulos */
        h1, h2, h3, h4, h5, h6 {
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 2. Configuração do Plotly para herdar o tema do Streamlit
    # Mudamos de "plotly_white" para "plotly_dark" ou deixamos o Streamlit gerenciar
    pio.templates.default = "plotly_dark" 
    
    # Dica extra: você pode customizar o layout global do Plotly aqui
    pio.templates["plotly_dark"].layout.paper_bgcolor = '#0e1117'
    pio.templates["plotly_dark"].layout.plot_bgcolor = '#0e1117'