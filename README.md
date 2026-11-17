# Saneamento básico e mortalidade infantil nos municípios brasileiros

**Global Solution — Desafio CitizenTech | Disciplina MLAM**
Coleta, organização e análise estatística de dados reais em Python.

Repositório: https://github.com/Pergola-code/gs-mlam-citizentech

## Integrante

| Nome completo | RM |
|---|---|
| Felipe Macedo | RM 570990 |

## Problema e objetivo das análises

**Problema.** A mortalidade infantil (óbitos de menores de um ano por mil nascidos vivos) é muito desigual entre os municípios brasileiros. Na média nacional o Brasil alcançou a meta dos Objetivos de Desenvolvimento do Milênio (15,7 por mil), mas médias nacionais escondem a realidade de cidades pequenas, do campo e de comunidades com pouca infraestrutura. Quem decide onde investir precisa saber **onde agir primeiro e sobre quais fatores**.

**Objetivo.** Usar dados públicos para responder a três perguntas:

1. A mortalidade infantil dos municípios predominantemente urbanos e dos predominantemente rurais difere da média nacional?
2. Quanto da variação da mortalidade infantil entre municípios está associado ao saneamento domiciliar, à educação e à renda?
3. Com esses três indicadores, é possível classificar os municípios que estão acima da meta, para apoiar a priorização de ações?

## Base de dados e fonte

| | |
|---|---|
| **Base** | Atlas do Desenvolvimento Humano no Brasil — indicadores municipais calculados a partir dos Censos Demográficos do IBGE |
| **Responsáveis pela base** | PNUD, Ipea e Fundação João Pinheiro (FJP) |
| **Endereço da base original** | http://www.atlasbrasil.org.br/ |
| **Cópia utilizada para o download** | https://github.com/abjur/abjData (arquivo `data/pnud_muni.rda`), redistribuição integral da base municipal do Atlas mantida pela Associação Brasileira de Jurimetria |
| **Natureza dos dados** | Dados reais e públicos. Nenhum registro foi gerado artificialmente. |
| **Base bruta** | `dados/brutos/atlas_brasil_municipios_1991_2000_2010.csv` — 16.695 linhas (5.565 municípios x 3 censos) e 125 colunas |
| **Base de análise** | `dados/base_municipios_2010.csv` — 5.565 municípios (Censo 2010) e 13 variáveis |
| **Dicionário de dados** | `dados/dicionario_variaveis.csv` |

### Limpeza, seleção e transformação (reproduzíveis)

Todas as etapas estão documentadas e são executadas por `codigos/01_preparacao_base.py`:

1. leitura da base bruta;
2. filtro do ano de 2010 (censo mais recente disponível no arquivo);
3. seleção das variáveis ligadas ao problema;
4. renomeação das colunas e padronização dos nomes dos municípios em maiúsculas;
5. criação de variáveis derivadas: sigla da UF, região, % de população urbana, perfil urbano/rural e indicador binário de mortalidade infantil acima da meta de 15,7 por mil;
6. verificações de qualidade (nenhum valor ausente, nenhum município duplicado, percentuais entre 0 e 100);
7. gravação da base de análise e do dicionário de dados.

Nenhum município foi excluído. A conversão da base original de `.rda` para `.csv`, sem alteração de conteúdo, está em `codigos/00_obter_base_bruta.py`.

### Variáveis usadas nas análises

| Variável | Código no Atlas | Descrição |
|---|---|---|
| `mort_infantil` | `mort1` | Crianças que não deverão sobreviver ao primeiro ano de vida, em cada 1.000 nascidas vivas |
| `pct_banheiro_agua` | `t_banagua` | % da população em domicílios com banheiro exclusivo e água encanada (saneamento domiciliar) |
| `taxa_analfabetismo` | `t_analf18m` | % de pessoas de 18 anos ou mais que não sabem ler nem escrever um bilhete simples |
| `renda_per_capita` | `rdpc` | Renda domiciliar per capita média mensal, em reais de agosto de 2010 |
| `alta_mortalidade` | derivada | 1 se `mort_infantil` > 15,7 (acima da meta); 0 caso contrário |
| `perfil` | derivada | Predominantemente urbano (≥ 80% de população urbana), predominantemente rural (< 50%) ou intermediário — critério operacional deste trabalho |

## Onde está cada entregável

```
.
├── README.md
├── requirements.txt
├── dados/
│   ├── brutos/atlas_brasil_municipios_1991_2000_2010.csv   base bruta (original, em .csv)
│   ├── base_municipios_2010.csv                            base utilizada nas análises
│   └── dicionario_variaveis.csv                            dicionário de dados
├── codigos/
│   ├── 00_obter_base_bruta.py          coleta: download e conversão da base original (opcional)
│   ├── 01_preparacao_base.py           limpeza, seleção e transformação
│   ├── 02_analise_estatistica.ipynb    análises dos itens 02 a 06, com as saídas preservadas
│   └── 03_gerar_relatorio.py           montagem do relatório em PDF
├── figuras/                            gráficos gerados pelo notebook
├── resultados/resultados.json          números calculados pelo notebook e usados no relatório
└── relatorio/relatorio_estatistico.pdf relatório estatístico (item 07)
```

| Item da avaliação | Onde encontrar |
|---|---|
| 01) Escolha da base de dados | Este README, `dados/` e seção 01 do notebook |
| 02) Distribuição Normal de Probabilidade | Notebook, seção 02 — relatório, seção 5.1 |
| 03) Testes de hipóteses para a média | Notebook, seção 03 — relatório, seção 5.2 |
| 04) Análise bivariada | Notebook, seção 04 — relatório, seção 5.3 |
| 05) Regressão linear múltipla | Notebook, seção 05 — relatório, seção 5.4 |
| 06) Regressão logística binária | Notebook, seção 06 — relatório, seção 5.5 |
| 07) Relatório estatístico | `relatorio/relatorio_estatistico.pdf` |

## Como executar os códigos

Requisito: Python 3.10 ou superior.

```bash
# 1. Clonar o repositório e entrar na pasta
git clone https://github.com/Pergola-code/gs-mlam-citizentech.git
cd gs-mlam-citizentech

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Gerar a base de análise a partir da base bruta
python codigos/01_preparacao_base.py

# 4. Executar as análises (gera as saídas, as figuras e o arquivo de resultados)
jupyter nbconvert --to notebook --execute --inplace codigos/02_analise_estatistica.ipynb
#    ou abrir o notebook no Jupyter/VS Code e usar "Run All"

# 5. Montar o relatório em PDF
python codigos/03_gerar_relatorio.py
```

Observações:

- O notebook já está salvo com todas as saídas; não é preciso executá-lo para conferir os resultados.
- O passo `python codigos/00_obter_base_bruta.py` é opcional, porque a base bruta já está no repositório. Ele precisa de internet e refaz a coleta do zero.
- Sorteios de amostras e a divisão treino/teste usam semente fixa (`SEMENTE = 42`); a execução reproduz exatamente os mesmos números.
- No Google Colab, envie a pasta `dados/` junto com o notebook, mantendo a estrutura de pastas.

## Bibliotecas e dependências

| Biblioteca | Uso | Versão utilizada |
|---|---|---|
| pandas | leitura e organização dos dados | 3.0.5 |
| numpy | cálculos numéricos | 2.5.3 |
| scipy | distribuição Normal, testes e correlação | 1.18.1 |
| statsmodels | regressões linear e logística, diagnósticos | 0.15.0 |
| scikit-learn | divisão treino/teste, matriz de confusão e acurácia | 1.9.1 |
| matplotlib e seaborn | gráficos | 3.11.2 e 0.13.2 |
| jupyter (nbconvert, ipykernel) | execução do notebook | — |
| reportlab | montagem do PDF (apenas `03_gerar_relatorio.py`) | 5.0.1 |
| pyreadr | conversão da base original (apenas `00_obter_base_bruta.py`) | 0.5.9 |

## Síntese dos principais resultados

Dados de 5.565 municípios (Censo 2010). Variável central: mortalidade infantil, com média de 19,25 e mediana de 16,90 óbitos por mil nascidos vivos.

| Item | Análise | Resultado |
|---|---|---|
| 02a | P(X < média), assumindo distribuição Normal | 0,5000 — evento tão provável quanto improvável |
| 02b | P(X > mediana), assumindo distribuição Normal | 0,6289 — evento provável |
| 03a | Teste Z, 20 municípios urbanos, H₁: μ < μ₀, α = 6% | média amostral 14,93; z = −2,70 (crítico −1,55); p = 0,0034; rejeita-se H₀ |
| 03b | Teste Z, 25 municípios rurais, H₁: μ > μ₀, α = 9% | média amostral 25,49; z = 4,37 (crítico 1,34); p < 0,0001; rejeita-se H₀ |
| 04 | Saneamento domiciliar x mortalidade infantil | covariância −114,58; r = −0,739; ŷ = 38,90 − 0,243·x; R² = 0,547; F = 6.711,0 |
| 05 | Regressão múltipla (saneamento, analfabetismo, renda) | R² = 0,723; R² ajustado = 0,723; F = 4.836,1 |
| 06 | Regressão logística (município acima da meta) | acurácia de 85,4% no teste; sensibilidade de 84,4%; especificidade de 86,7% |

Principais conclusões:

- 58,5% dos municípios estavam acima da meta de 15,7 por mil; no Nordeste, 99,0%; no Sul, 11,8%.
- Municípios predominantemente rurais têm mortalidade infantil média de 22,1 por mil, contra 15,5 nos predominantemente urbanos; os testes de hipóteses confirmaram as diferenças em relação à média nacional.
- O saneamento domiciliar tem correlação forte e negativa com a mortalidade infantil e, sozinho, explica 54,7% da sua variação.
- Com educação e renda no modelo, a explicação sobe para 72,3% e o analfabetismo adulto é o fator de maior peso; o coeficiente do saneamento cai 67%, sinal de que parte da sua associação era compartilhada com os outros dois fatores.
- Com apenas três indicadores, a regressão logística classifica corretamente 85,4% dos municípios quanto ao cumprimento da meta, o que permite uma triagem inicial de municípios prioritários.

## Limitações identificadas

- **Dados de 2010:** a situação atual dos municípios pode ser diferente.
- **Mortalidade infantil estimada:** no Atlas, o indicador municipal é obtido por métodos demográficos indiretos a partir do Censo, e não pela contagem direta de óbitos; parte da associação observada pode refletir o próprio método de estimação.
- **Associação não é causalidade:** os dados são observacionais e de um único ano; fatores não incluídos (como acesso a serviços de saúde) podem explicar parte das relações.
- **Dados agregados:** as conclusões valem para municípios, não para famílias ou pessoas, e cada município tem o mesmo peso.
- **Alcance do indicador de saneamento:** mede banheiro exclusivo e água encanada no domicílio; não informa sobre rede coletora, tratamento de esgoto ou qualidade da água.
- **Hipótese de normalidade (itens 02 e 03):** a mortalidade infantil é assimétrica à direita; as probabilidades calculadas são aproximações.
- **Linearidade e heterocedasticidade:** as relações com saneamento e renda são curvas em parte da faixa e os resíduos têm variância não constante.
- **Dependência espacial:** municípios vizinhos se parecem, o que tende a tornar os p-valores otimistas.
- **Critérios adotados:** o corte binário na meta e os limites de 80% e 50% para definir municípios urbanos e rurais são escolhas operacionais.

## Referências

- PNUD; Ipea; FJP. *Atlas do Desenvolvimento Humano no Brasil*. Disponível em: http://www.atlasbrasil.org.br/.
- PNUD; Ipea; FJP. *O Índice de Desenvolvimento Humano Municipal Brasileiro*. Brasília: PNUD, Ipea, FJP, 2013.
- Ipea; SPI/MP. *Objetivos de Desenvolvimento do Milênio: relatório nacional de acompanhamento*. Brasília: Ipea, 2014.
- Associação Brasileira de Jurimetria. *abjData*. Disponível em: https://github.com/abjur/abjData.
