from pathlib import Path

# pasta base do projeto
BASE_DIR = Path(__file__).resolve().parent

# estrutura de pastas
estrutura = [
    "dashboard",
    "dashboard/config",
    "dashboard/data",
    "dashboard/services",
    "dashboard/charts",
    "dashboard/ui",
]

# arquivos iniciais
arquivos = {
    "dashboard/config/theme.py": "",
    "dashboard/data/loader.py": "",
    "dashboard/services/metrics.py": "",
    "dashboard/services/transforms.py": "",
    "dashboard/charts/gauge.py": "",
    "dashboard/charts/line_oee.py": "",
    "dashboard/charts/heatmap_linha_hora.py": "",
    "dashboard/charts/turno_chart.py": "",
    "dashboard/ui/filters.py": "",
}

def criar_estrutura():

    print("\nCriando estrutura do dashboard...\n")

    # criar pastas
    for pasta in estrutura:

        caminho = BASE_DIR / pasta
        caminho.mkdir(parents=True, exist_ok=True)

        print(f"✓ Pasta criada: {pasta}")

    # criar arquivos
    for arquivo, conteudo in arquivos.items():

        caminho = BASE_DIR / arquivo

        if not caminho.exists():
            caminho.write_text(conteudo, encoding="utf-8")
            print(f"✓ Arquivo criado: {arquivo}")
        else:
            print(f"- Arquivo já existe: {arquivo}")

    print("\nEstrutura do dashboard criada com sucesso.\n")


if __name__ == "__main__":
    criar_estrutura()