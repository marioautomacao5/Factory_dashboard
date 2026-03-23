import duckdb
import os

BASE_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_CONSULTA = os.path.join(BASE_PROJETO, "data", "warehouse", "producao.duckdb")


def resetar_banco(confirmar=False):

    if not confirmar:
        print("⚠️ Operação cancelada. Passe confirmar=True para executar.")
        return

    if not os.path.exists(DB_CONSULTA):
        print("Banco não encontrado.")
        return

    con = duckdb.connect(DB_CONSULTA)

    # 🔥 lista completa de tabelas do projeto
    tabelas = [
        "paradas_historico",
        "paradas_consulta",
        "producao_historico",
        "producao_consulta"
    ]

    for tabela in tabelas:
        try:
            con.execute(f"DROP TABLE IF EXISTS {tabela}")
            print(f"✔ Tabela removida: {tabela}")
        except Exception as e:
            print(f"Erro ao remover {tabela}: {e}")

    con.close()

    print("🔥 Reset completo do banco finalizado.")

resetar_banco(confirmar=True)