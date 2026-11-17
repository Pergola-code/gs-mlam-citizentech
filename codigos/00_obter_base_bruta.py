"""
00_obter_base_bruta.py
----------------------
Etapa OPCIONAL: a base bruta já está versionada em dados/brutos/, então este
script só precisa ser executado por quem quiser refazer a coleta do zero.

O que ele faz: baixa a base municipal do Atlas do Desenvolvimento Humano no
Brasil (PNUD, Ipea e FJP - Censos Demográficos de 1991, 2000 e 2010) e a
converte, SEM NENHUMA ALTERAÇÃO de conteúdo, do formato .rda (R) para .csv.

Fonte original dos dados:
    Atlas do Desenvolvimento Humano no Brasil - PNUD, Ipea e FJP
    http://www.atlasbrasil.org.br/

Cópia utilizada para o download (redistribuição integral da base municipal do
Atlas, mantida pela Associação Brasileira de Jurimetria no pacote abjData):
    https://github.com/abjur/abjData  (arquivo data/pnud_muni.rda)

Requisitos extras desta etapa: internet e a biblioteca pyreadr
    pip install pyreadr

Uso (a partir da raiz do repositório):
    python codigos/00_obter_base_bruta.py
"""
from pathlib import Path
from urllib.request import urlretrieve

import pyreadr

URL_RDA = "https://raw.githubusercontent.com/abjur/abjData/master/data/pnud_muni.rda"

RAIZ = Path(__file__).resolve().parents[1]
PASTA_BRUTOS = RAIZ / "dados" / "brutos"
ARQ_RDA = PASTA_BRUTOS / "pnud_muni.rda"
ARQ_CSV = PASTA_BRUTOS / "atlas_brasil_municipios_1991_2000_2010.csv"


def main() -> None:
    PASTA_BRUTOS.mkdir(parents=True, exist_ok=True)

    if not ARQ_RDA.exists():
        print(f"Baixando {URL_RDA} ...")
        urlretrieve(URL_RDA, ARQ_RDA)

    # O arquivo .rda contém um único data frame, chamado 'pnud_muni'
    base = pyreadr.read_r(str(ARQ_RDA))["pnud_muni"]

    # Apenas conversão de formato: nenhuma linha ou coluna é alterada aqui
    base.to_csv(ARQ_CSV, index=False, encoding="utf-8")
    ARQ_RDA.unlink()  # mantemos somente o .csv no repositório

    print(f"Base bruta salva em: {ARQ_CSV.relative_to(RAIZ)}")
    print(f"Dimensões: {base.shape[0]} linhas x {base.shape[1]} colunas")
    print(f"Anos disponíveis: {sorted(base['ano'].unique().tolist())}")


if __name__ == "__main__":
    main()
