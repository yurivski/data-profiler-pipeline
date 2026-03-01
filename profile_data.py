# Script para gerar perfil de dados com validação de qualidade.

import pandas as pd
from ydata_profiling import ProfileReport
from pathlib import Path
from datetime import datetime

csv_file = '20260228_Pedidos_csv_2025.csv'

max_duplicates_pct = 5.0 # %
max_missing_pct = 10.0 # %

# pasta para salvar os relatórios
reports_dir = 'reports'

# TODO:
def carregar_dados(caminho):
    df = pd.read_csv(caminho)
    return df

def gerar_relatorios(df, titulo=None):
    if titulo is None:
        titulo = f"Profile {datetime.now():%Y-%m-%d %H:%M}"

        # True = rápido, menos detalhes / False = mais lento e mais completo
        profile = ProfileReport(
            df,
            title=titulo,
            minimal=False
        )

        arquivo = f"{reports_dir}/relatorio_{datetime.now():%Y%m%d}.html"
        profile.to_file(arquivo)
        return profile

def extrair_estatisticas(profile):
    desc = profile.get_description()
    tabela = desc['table']

    stats = {
        'total_linhas': tabela['n'],
        'total_colunas': tabela['n_var'],
        'duplicatas': tabela['n_duplicates'],
        'pct_dublicatas': (tabela['n_duplicates'] / tabela['n'] * 100) if tabela['n'] > 0 else 0,
        'valores_faltantes': tabela['n_cells_missing'],
        'pct_faltantes': tabela['p_cells_missings'] * 100,
    }
    return stats

def validar_qualidade(stats, max_dup=max_duplicates_pct, max_miss=max_missing_pct):
    aprovado = True
    if stats['pct_duplicates'] > max_dup:
        print(f"Falha: Limite é {max_dup}%")
        aprovado = False
    else:
        print(f"Ok: Abaixo do limite de {max_dup}%")

    if stats['pct_faltantes'] > max_miss:
        print(f" Falha: limite é {max_miss}%")
        aprovado = False
    else:
        printprint(f"Ok: Abaixo do limite de {max_miss}%")

    if aprovado:
        print("Dados carregados")
    else:
        print("Dados não carregados")
    return aprovado

def main():
    fd = carregar_dados(csv_file)
    profile = gerar_relatorios(df, titulo="Análise de Dados")
    stats = extrair_estatisticas(profile)
    passou = validar_qualidade(stats)
    return 0 if passou else 1

if __name__ == '__main__':
    exit(main())