import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path

print("Scheduler ETL iniciado")

BASE_DIR = Path(__file__).resolve().parents[1]
PYTHON_EXEC = sys.executable

# controle de execução
ultimo_run_paradas = 0
intervalo_paradas = 300  # 5 minutos (300 segundos)

while True:

    agora = time.time()

    print(f"\n[{datetime.now()}] Executando ETL produção")

    # 🔵 ETL PRODUÇÃO (1 min)
    subprocess.run(
        [PYTHON_EXEC, str(BASE_DIR / "scripts" / "run_pipeline.py")],
        cwd=BASE_DIR
    )

    # 🔴 ETL PARADAS (5 min)
    if agora - ultimo_run_paradas >= intervalo_paradas:

        print(f"[{datetime.now()}] Executando ETL paradas")

        subprocess.run(
            [PYTHON_EXEC, str(BASE_DIR / "scripts" / "run_pipeline_paradas.py")],
            cwd=BASE_DIR
        )

        ultimo_run_paradas = agora

    print(f"[{datetime.now()}] Ciclo finalizado")

    time.sleep(60)