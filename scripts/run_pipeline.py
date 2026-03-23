import os
import sys

# ======================================================
# EXECUTAR
# ======================================================

# adiciona raiz do projeto ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from pipeline.pipeline import executar_etl

if __name__ == "__main__":
    executar_etl()