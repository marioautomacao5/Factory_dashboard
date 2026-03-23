import streamlit as st


def aplicar_tema():

    st.markdown(
        """
        <style>

        .stApp {
            background-color: #0e1117;
            color: white;
        }

        div[data-testid="metric-container"] {
            background-color: #1b1f2a;
            padding: 15px;
            border-radius: 10px;
        }

        /* Títulos */
        h1, h2, h3, h4, h5, h6 {
            color: white;
        }

        /* Ticks de eixo dos gráficos */
        div[class*="main"] svg text {
            fill: white !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )