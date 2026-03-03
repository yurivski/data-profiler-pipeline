"""
Script de validação de qualidade de dados usando ydata-profiling.

Gera relatório HTML interativo com estatísticas descritivas,
alertas de qualidade e visualizações automáticas.
"""

import pandas as pd
import glob
import os
from ydata_profiling import ProfileReport
from pathlib import Path
from datetime import datetime

# Diretório e padrão do arquivo CSV a ser analisado
file_dir = 'Arquivos_csv_2025'
file_pattern = "20260228_Pedidos_csv_2025.csv"

# Limites de qualidade para aprovação do dataset
max_duplicates_pct = 5.0 # máximo de duplicatas permitido (%)
max_missing_pct = 10.0 # máximo de valores faltantes permitido (%)

# Diretório onde relatórios HTML serão salvos
reports_dir = 'reports'

# Carrega CSV com encoding UTF-16 e separador ponto e vírgula.
# Para CSVs normais (UTF-8, vírgula), remova os parâmetros encoding e sep.
def carregar_dados(caminho):
    df = pd.read_csv(
        caminho,
        sep=';', 
        encoding='utf-16', 
        engine='python',
        on_bad_lines='skip'
    )
    return df

# Gera relatório HTML com ydata-profiling.
def gerar_relatorios(df, titulo=None):
    # Define o título interno
    if titulo is None:
        titulo = f"Profile {datetime.now():%Y-%m-%d %H:%M}"

        # True = rápido, menos detalhes / False = mais lento e mais completo
    profile = ProfileReport(
        df,
        title=titulo,
        minimal=False
    )
    # Define o nome do arquivo salvo
    arquivo = f"{reports_dir}/relatorio_{datetime.now():%Y%m%d}.html"
    profile.to_file(arquivo)
    return profile

# Extrai estatísticas do relatório para validação.
def extrair_estatisticas(profile):
    desc = profile.get_description()

    # Detectar se desc.table é acessível como atributo ou dict
    # Versões antigas: desc é dict
    if hasattr(desc, 'table'):
        tabela = desc.table
    else:
        tabela = desc['table']

     # Detectar se tabela é dict ou objeto
    if isinstance(tabela, dict):
        stats = {
            'total_linhas': tabela['n'],
            'total_colunas': tabela['n_var'],
            'duplicates': tabela['n_duplicates'],
            'pct_duplicates': (tabela['n_duplicates'] / tabela['n'] * 100) if tabela['n'] > 0 else 0,
            'valores_faltantes': tabela['n_cells_missing'],
            'pct_faltantes': tabela['p_cells_missing'] * 100,
            }
    else:
        stats = {
            'total_linhas': tabela.n,
            'total_colunas': tabela.n_var,
            'duplicates': tabela.n_duplicates,
            'pct_duplicates': (tabela.n_duplicates / tabela.n * 100) if tabela.n > 0 else 0,
            'valores_faltantes': tabela.n_cells_missing,
            'pct_faltantes': tabela.p_cells_missing * 100,
        }
    return stats

# Valida estatísticas contra thresholds de qualidade.
def validar_qualidade(stats, max_dup=max_duplicates_pct, max_miss=max_missing_pct):
    aprovado = True

    # Validar duplicatas
    if stats['pct_duplicates'] > max_dup:
        print(f"Falha: Limite é {max_dup}%")
        aprovado = False
    else:
        print(f"Ok: Abaixo do limite de {max_dup}%")

    # Validar valores faltantes
    if stats['pct_faltantes'] > max_miss:
        print(f" Falha: limite é {max_miss}%")
        aprovado = False
    else:
        print(f"Ok: Abaixo do limite de {max_miss}%")

    # Resultado final
    if aprovado:
        print("Dados podem ser carregados")
    else:
        print("Corrigir problemas antes de carregar")
    return aprovado

def main():
    # Encontrar arquivo CSV
    pattern = os.path.join(file_dir, file_pattern)
    arquivos = glob.glob(pattern)
    csv_file = arquivos[0]

    # Validação
    df = carregar_dados(csv_file)
    profile = gerar_relatorios(df, titulo="Análise de Pedidos 2025")
    stats = extrair_estatisticas(profile)
    passou = validar_qualidade(stats)
    return 0 if passou else 1

if __name__ == '__main__':
    exit(main())