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
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #2d323e;
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