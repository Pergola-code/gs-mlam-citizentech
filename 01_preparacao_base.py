"""
01_preparacao_base.py
---------------------
Limpeza, seleção e transformação da base bruta do Atlas do Desenvolvimento
Humano no Brasil, gerando a base usada em todas as análises.

Entrada : dados/brutos/atlas_brasil_municipios_1991_2000_2010.csv
          (16.695 linhas = 5.565 municípios x 3 censos; 125 colunas)
Saídas  : dados/base_municipios_2010.csv   (base de análise)
          dados/dicionario_variaveis.csv   (dicionário de dados)

Etapas (todas reproduzíveis por este script):
    1. Leitura da base bruta.
    2. Filtro do ano de 2010 (censo mais recente disponível na base).
    3. Seleção das variáveis ligadas ao problema (saneamento, educação,
       renda, urbanização e mortalidade infantil).
    4. Renomeação das colunas para nomes autoexplicativos e padronização dos
       nomes dos municípios em letras maiúsculas.
    5. Criação de variáveis derivadas (região, sigla da UF, % de população
       urbana, perfil urbano/rural e indicador binário de alta mortalidade).
    6. Verificações de qualidade (ausentes, duplicados e faixas válidas).
    7. Gravação da base de análise e do dicionário de variáveis.

Uso (a partir da raiz do repositório):
    python codigos/01_preparacao_base.py
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
ARQ_BRUTO = RAIZ / "dados" / "brutos" / "atlas_brasil_municipios_1991_2000_2010.csv"
ARQ_BASE = RAIZ / "dados" / "base_municipios_2010.csv"
ARQ_DICIONARIO = RAIZ / "dados" / "dicionario_variaveis.csv"

ANO_ANALISE = 2010

# Meta dos Objetivos de Desenvolvimento do Milênio (ODM 4) para a mortalidade
# infantil no Brasil: 15,7 óbitos por mil nascidos vivos até 2015
# (Ipea/SPI, Relatório Nacional de Acompanhamento dos ODM, 2014).
META_ODM_MORTALIDADE_INFANTIL = 15.7

# Critério operacional adotado neste trabalho para o perfil dos municípios
LIMITE_URBANO = 80.0  # >= 80% da população em área urbana
LIMITE_RURAL = 50.0   # <  50% da população em área urbana

# Código original no Atlas -> nome usado na base de análise
RENOMEAR = {
    "codmun7": "cod_municipio",
    "municipio": "municipio",
    "ufn": "nome_uf",
    "pesotot": "populacao",
    "mort1": "mort_infantil",
    "t_banagua": "pct_banheiro_agua",
    "t_analf18m": "taxa_analfabetismo",
    "rdpc": "renda_per_capita",
}

# Código IBGE da UF -> sigla
SIGLA_UF = {
    11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO",
    21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL",
    28: "SE", 29: "BA", 31: "MG", 32: "ES", 33: "RJ", 35: "SP", 41: "PR",
    42: "SC", 43: "RS", 50: "MS", 51: "MT", 52: "GO", 53: "DF",
}

# Primeiro dígito do código da UF -> grande região
REGIAO = {1: "Norte", 2: "Nordeste", 3: "Sudeste", 4: "Sul", 5: "Centro-Oeste"}

DICIONARIO = [
    ("cod_municipio", "codmun7", "Código IBGE do município (7 dígitos).", "identificador"),
    ("municipio", "municipio", "Nome do município.", "texto"),
    ("uf", "uf (derivada)", "Sigla da Unidade da Federação, obtida do código IBGE da UF.", "texto"),
    ("nome_uf", "ufn", "Nome da Unidade da Federação.", "texto"),
    ("regiao", "uf (derivada)", "Grande região, obtida do primeiro dígito do código da UF.", "texto"),
    ("populacao", "pesotot", "População total do município no Censo 2010.", "habitantes"),
    ("pct_pop_urbana", "pesourb / pesotot (derivada)",
     "Percentual da população residente em área urbana = 100 x pesourb / pesotot.", "%"),
    ("perfil", "derivada",
     "Perfil do município pelo critério adotado neste trabalho: 'Predominantemente urbano' (pct_pop_urbana >= 80), "
     "'Predominantemente rural' (pct_pop_urbana < 50) ou 'Intermediário'.", "texto"),
    ("mort_infantil", "mort1",
     "Mortalidade infantil: número de crianças que não deverão sobreviver ao primeiro ano de vida "
     "em cada 1.000 nascidas vivas.", "óbitos por mil nascidos vivos"),
    ("pct_banheiro_agua", "t_banagua",
     "Percentual da população que vive em domicílios com banheiro e água encanada.", "%"),
    ("taxa_analfabetismo", "t_analf18m",
     "Taxa de analfabetismo da população de 18 anos ou mais de idade.", "%"),
    ("renda_per_capita", "rdpc",
     "Renda domiciliar per capita média mensal, em reais de agosto de 2010.", "R$"),
    ("alta_mortalidade", "mort1 (derivada)",
     "Indicador binário: 1 se mort_infantil > 15,7 (acima da meta ODM para o Brasil), 0 caso contrário.",
     "0/1"),
]


def main() -> None:
    # 1. Leitura da base bruta -------------------------------------------------
    bruta = pd.read_csv(ARQ_BRUTO)
    print(f"[1] Base bruta: {bruta.shape[0]} linhas x {bruta.shape[1]} colunas")

    # 2. Filtro do ano ---------------------------------------------------------
    base = bruta.loc[bruta["ano"] == ANO_ANALISE].copy()
    print(f"[2] Registros de {ANO_ANALISE}: {len(base)} municípios")

    # 3 e 5. Variáveis derivadas que dependem de colunas originais --------------
    base["sigla_uf"] = base["uf"].map(SIGLA_UF)
    base["regiao"] = (base["uf"] // 10).map(REGIAO)
    base["pct_pop_urbana"] = (100 * base["pesourb"] / base["pesotot"]).round(2)

    # 3 e 4. Seleção e renomeação ----------------------------------------------
    base = base.rename(columns=RENOMEAR)
    # Padronização: a base bruta traz alguns nomes de municípios em minúsculas
    base["municipio"] = base["municipio"].str.upper().str.strip()
    base = base.drop(columns=["uf"]).rename(columns={"sigla_uf": "uf"})

    # 5. Demais variáveis derivadas --------------------------------------------
    base["perfil"] = "Intermediário"
    base.loc[base["pct_pop_urbana"] >= LIMITE_URBANO, "perfil"] = "Predominantemente urbano"
    base.loc[base["pct_pop_urbana"] < LIMITE_RURAL, "perfil"] = "Predominantemente rural"
    base["alta_mortalidade"] = (base["mort_infantil"] > META_ODM_MORTALIDADE_INFANTIL).astype(int)

    colunas = [nome for nome, *_ in DICIONARIO]
    base = base[colunas].sort_values("cod_municipio").reset_index(drop=True)
    print(f"[3-5] Variáveis selecionadas/derivadas: {len(colunas)}")

    # 6. Verificações de qualidade ---------------------------------------------
    ausentes = int(base.isna().sum().sum())
    duplicados = int(base["cod_municipio"].duplicated().sum())
    assert ausentes == 0, "Há valores ausentes na base de análise."
    assert duplicados == 0, "Há municípios duplicados na base de análise."
    for coluna in ["pct_pop_urbana", "pct_banheiro_agua", "taxa_analfabetismo"]:
        assert base[coluna].between(0, 100).all(), f"{coluna} fora da faixa 0-100."
    assert (base["mort_infantil"] > 0).all() and (base["renda_per_capita"] > 0).all()
    assert base["regiao"].notna().all() and base["uf"].notna().all()
    print(f"[6] Valores ausentes: {ausentes} | municípios duplicados: {duplicados} | faixas válidas: OK")

    # 7. Gravação --------------------------------------------------------------
    base.to_csv(ARQ_BASE, index=False, encoding="utf-8")
    dicionario = pd.DataFrame(
        DICIONARIO, columns=["variavel", "codigo_no_atlas", "descricao", "unidade"]
    )
    dicionario.to_csv(ARQ_DICIONARIO, index=False, encoding="utf-8")
    print(f"[7] Base de análise salva em: {ARQ_BASE.relative_to(RAIZ)} "
          f"({base.shape[0]} linhas x {base.shape[1]} colunas)")
    print(f"    Dicionário salvo em: {ARQ_DICIONARIO.relative_to(RAIZ)}")
    print("\nMunicípios por região:")
    print(base["regiao"].value_counts().to_string())
    print("\nMunicípios por perfil:")
    print(base["perfil"].value_counts().to_string())
    print(f"\nMunicípios acima da meta ODM ({META_ODM_MORTALIDADE_INFANTIL} por mil): "
          f"{base['alta_mortalidade'].sum()} ({100 * base['alta_mortalidade'].mean():.1f}%)")


if __name__ == "__main__":
    main()
