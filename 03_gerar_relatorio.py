"""
03_gerar_relatorio.py
---------------------
Monta o relatório estatístico (item 07) em PDF a partir dos resultados gerados
pelo notebook 02_analise_estatistica.ipynb.

Entradas : resultados/resultados.json  (números calculados no notebook)
           figuras/fig01 ... fig10     (gráficos gerados no notebook)
Saída    : relatorio/relatorio_estatistico.pdf

Todos os números do relatório são lidos do arquivo de resultados, de modo que
o texto do PDF nunca diverge do que foi calculado no notebook.

Requisito extra desta etapa: reportlab  (pip install reportlab)

Uso (a partir da raiz do repositório, depois de executar o notebook):
    python codigos/03_gerar_relatorio.py
"""
import json
from pathlib import Path

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

# ----------------------------------------------------------------------------
# Identificação (trabalho individual)
# ----------------------------------------------------------------------------
INTEGRANTES = [
    ("Felipe Macedo", "RM 570990"),
]
DATA_RELATORIO = "Novembro de 2026"

RAIZ = Path(__file__).resolve().parents[1]
FIGURAS = RAIZ / "figuras"
SAIDA = RAIZ / "relatorio" / "relatorio_estatistico.pdf"
R = json.loads((RAIZ / "resultados" / "resultados.json").read_text(encoding="utf-8"))

# ----------------------------------------------------------------------------
# Fontes (DejaVu Sans, distribuída com o matplotlib: acentos e símbolos)
# ----------------------------------------------------------------------------
PASTA_FONTES = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
pdfmetrics.registerFont(TTFont("Texto", str(PASTA_FONTES / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("Texto-Negrito", str(PASTA_FONTES / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Texto-Italico", str(PASTA_FONTES / "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("Texto-NegritoItalico", str(PASTA_FONTES / "DejaVuSans-BoldOblique.ttf")))
pdfmetrics.registerFontFamily("Texto", normal="Texto", bold="Texto-Negrito",
                              italic="Texto-Italico", boldItalic="Texto-NegritoItalico")

# ----------------------------------------------------------------------------
# Estilos
# ----------------------------------------------------------------------------
TINTA = colors.HexColor("#0b0b0b")
TINTA2 = colors.HexColor("#52514e")
AZUL = colors.HexColor("#184f95")
AZUL_FUNDO = colors.HexColor("#eef4fd")
LINHA = colors.HexColor("#c3c2b7")
LARGURA_UTIL = A4[0] - 4 * cm

E = {
    "capa_sup": ParagraphStyle("capa_sup", fontName="Texto-Negrito", fontSize=10.5, leading=14,
                               textColor=AZUL, alignment=TA_LEFT),
    "capa_titulo": ParagraphStyle("capa_titulo", fontName="Texto-Negrito", fontSize=25, leading=31,
                                  textColor=TINTA, alignment=TA_LEFT),
    "capa_sub": ParagraphStyle("capa_sub", fontName="Texto", fontSize=13, leading=18,
                               textColor=TINTA2, alignment=TA_LEFT),
    "capa_txt": ParagraphStyle("capa_txt", fontName="Texto", fontSize=10.5, leading=15,
                               textColor=TINTA, alignment=TA_LEFT),
    "h1": ParagraphStyle("h1", fontName="Texto-Negrito", fontSize=14, leading=18, textColor=AZUL,
                         spaceBefore=14, spaceAfter=6, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Texto-Negrito", fontSize=11, leading=14, textColor=TINTA,
                         spaceBefore=10, spaceAfter=4, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Texto", fontSize=9.3, leading=13.6, textColor=TINTA,
                        alignment=TA_JUSTIFY, spaceAfter=6),
    "item": ParagraphStyle("item", fontName="Texto", fontSize=9.3, leading=13.6, textColor=TINTA,
                           alignment=TA_JUSTIFY, leftIndent=14, bulletIndent=2, spaceAfter=3.5),
    "eq": ParagraphStyle("eq", fontName="Texto-Negrito", fontSize=9.6, leading=14, textColor=TINTA,
                         alignment=TA_CENTER, spaceBefore=3, spaceAfter=8, backColor=AZUL_FUNDO,
                         borderPadding=(6, 6, 6, 6)),
    "legenda": ParagraphStyle("legenda", fontName="Texto-Italico", fontSize=8, leading=10.5,
                              textColor=TINTA2, alignment=TA_CENTER, spaceBefore=3, spaceAfter=9),
    "cel": ParagraphStyle("cel", fontName="Texto", fontSize=8.2, leading=10.6, textColor=TINTA),
    "cel_c": ParagraphStyle("cel_c", fontName="Texto", fontSize=8.2, leading=10.6, textColor=TINTA,
                            alignment=TA_CENTER),
    "cel_h": ParagraphStyle("cel_h", fontName="Texto-Negrito", fontSize=8.2, leading=10.6,
                            textColor=TINTA, alignment=TA_CENTER),
    "cel_hl": ParagraphStyle("cel_hl", fontName="Texto-Negrito", fontSize=8.2, leading=10.6,
                             textColor=TINTA),
    "ref": ParagraphStyle("ref", fontName="Texto", fontSize=8.6, leading=12, textColor=TINTA,
                          alignment=TA_LEFT, spaceAfter=5),
}


# ----------------------------------------------------------------------------
# Funções auxiliares
# ----------------------------------------------------------------------------
def br(valor, casas=2, sinal=False):
    """Número no padrão brasileiro (vírgula decimal, ponto de milhar)."""
    texto = f"{valor:+,.{casas}f}" if sinal else f"{valor:,.{casas}f}"
    return texto.replace(",", "§").replace(".", ",").replace("§", ".").replace("-", "−")


def fmt_p(p, com_sinal=True):
    if p < 0.0001:
        return "&lt; 0,0001"
    return ("= " if com_sinal else "") + br(p, 4)


def inteiro(valor):
    return f"{int(valor):,}".replace(",", ".")


def P(texto, estilo="p"):
    return Paragraph(texto, E[estilo])


def itens(lista):
    return [Paragraph(texto, E["item"], bulletText="•") for texto in lista]


CONTADOR = {"figura": 0, "tabela": 0}


def legenda(tipo, texto):
    CONTADOR[tipo] += 1
    nome = "Figura" if tipo == "figura" else "Tabela"
    return Paragraph(f"<b>{nome} {CONTADOR[tipo]}</b> — {texto}", E["legenda"])


def imagem(nome, largura):
    caminho = FIGURAS / nome
    largura_px, altura_px = ImageReader(str(caminho)).getSize()
    return Image(str(caminho), width=largura, height=largura * altura_px / largura_px)


def figura(nome, largura_cm, texto):
    return KeepTogether([imagem(nome, largura_cm * cm), legenda("figura", texto)])


def figuras_lado_a_lado(nome_1, nome_2, largura_1_cm, largura_2_cm, texto):
    linha = Table([[imagem(nome_1, largura_1_cm * cm), imagem(nome_2, largura_2_cm * cm)]],
                  colWidths=[(largura_1_cm + 0.3) * cm, (largura_2_cm + 0.3) * cm])
    linha.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    return KeepTogether([linha, legenda("figura", texto)])


def tabela(linhas, larguras_cm, texto, primeira_coluna_esquerda=True, cabecalho_esquerda=False, antes=None,
           pode_dividir=False):
    """Tabela com cabeçalho destacado; 'linhas' é uma lista de listas de textos.

    'antes' recebe elementos (um título de seção, por exemplo) que devem ficar na mesma página da tabela.
    """
    for j, celula in enumerate(linhas[0]):          # nenhuma palavra do cabeçalho pode ser maior que a coluna
        for palavra in str(celula).replace("<sub>", "").replace("</sub>", "").split():
            largura_palavra = pdfmetrics.stringWidth(palavra, "Texto-Negrito", 8.2)
            assert largura_palavra <= larguras_cm[j] * cm - 10, f"Coluna estreita para '{palavra}' em: {texto}"
    dados = []
    for i, linha in enumerate(linhas):
        nova = []
        for j, celula in enumerate(linha):
            if i == 0:
                estilo = "cel_hl" if (cabecalho_esquerda and j == 0) else "cel_h"
            else:
                estilo = "cel" if (primeira_coluna_esquerda and j == 0) else "cel_c"
            nova.append(Paragraph(str(celula), E[estilo]))
        dados.append(nova)
    t = Table(dados, colWidths=[l * cm for l in larguras_cm], repeatRows=1, hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_FUNDO),
        ("LINEABOVE", (0, 0), (-1, 0), 0.9, AZUL),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, AZUL),
        ("LINEBELOW", (0, 1), (-1, -2), 0.3, LINHA),
        ("LINEBELOW", (0, -1), (-1, -1), 0.9, AZUL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))
    bloco = (antes or []) + [legenda("tabela", texto), t, Spacer(1, 9)]
    if pode_dividir:                 # tabela longa: pode continuar na página seguinte (cabeçalho repetido)
        return bloco
    return KeepTogether(bloco)


def cabecalho_rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Texto", 7.6)
    canvas.setFillColor(TINTA2)
    canvas.drawString(2 * cm, A4[1] - 1.25 * cm, "Relatório estatístico · Saneamento e mortalidade infantil nos municípios brasileiros")
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.25 * cm, "CitizenTech · MLAM")
    canvas.setStrokeColor(LINHA)
    canvas.setLineWidth(0.4)
    canvas.line(2 * cm, A4[1] - 1.4 * cm, A4[0] - 2 * cm, A4[1] - 1.4 * cm)
    canvas.drawCentredString(A4[0] / 2, 1.1 * cm, f"Página {doc.page}")
    canvas.restoreState()


def capa(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(AZUL)
    canvas.rect(0, A4[1] - 1.1 * cm, A4[0], 1.1 * cm, stroke=0, fill=1)
    canvas.restoreState()


# ----------------------------------------------------------------------------
# Atalhos para os resultados
# ----------------------------------------------------------------------------
G = R["geral"]
D = R["descritivas"]
REG = R["por_regiao"]
PERF = R["por_perfil"]
R2, R3, R4, R5, R6 = R["item02"], R["item03"], R["item04"], R["item05"], R["item06"]
TA, TB = R3["a"], R3["b"]
FAIXAS = list(R["item04_faixas"].values())
META = br(G["meta_odm"], 1)
URB, RUR = PERF["Predominantemente urbano"], PERF["Predominantemente rural"]
N_BAIXA_COBERTURA = FAIXAS[0]["municipios"] + FAIXAS[1]["municipios"]      # até 60% de cobertura
COEF, BETA, LOGI = R5["coef"], R5["betas"], R6["coef"]
REDUCAO_SANEAMENTO = 100 * (1 - COEF["pct_banheiro_agua"] / R4["b1"])
N_TESTE = R6["n_teste"]
ROTULO = {"pct_banheiro_agua": "Saneamento domiciliar (% com banheiro e água encanada)",
          "taxa_analfabetismo": "Analfabetismo adulto (%)",
          "renda_per_capita": "Renda per capita (R$)"}
CURTO = {"mort_infantil": "Mortalidade infantil", "pct_banheiro_agua": "Saneamento",
         "taxa_analfabetismo": "Analfabetismo", "renda_per_capita": "Renda"}
VARS = ["mort_infantil", "pct_banheiro_agua", "taxa_analfabetismo", "renda_per_capita"]

decisao_a = "Rejeita-se H<sub>0</sub>" if TA["rejeita_h0"] else "Não se rejeita H<sub>0</sub>"
decisao_b = "Rejeita-se H<sub>0</sub>" if TB["rejeita_h0"] else "Não se rejeita H<sub>0</sub>"

# ----------------------------------------------------------------------------
# Conteúdo
# ----------------------------------------------------------------------------
H = []

# ---- Capa -------------------------------------------------------------------
H += [
    Spacer(1, 4.2 * cm),
    P("RELATÓRIO ESTATÍSTICO · GLOBAL SOLUTION · DESAFIO CITIZENTECH", "capa_sup"),
    Spacer(1, 0.5 * cm),
    P("Saneamento básico e mortalidade infantil nos municípios brasileiros", "capa_titulo"),
    Spacer(1, 0.5 * cm),
    P("Evidências estatísticas para priorizar ações em cidades, no campo e em comunidades", "capa_sub"),
    Spacer(1, 2.2 * cm),
    P("<b>Disciplina:</b> MLAM", "capa_txt"),
    P("<b>Base de dados:</b> Atlas do Desenvolvimento Humano no Brasil (PNUD, Ipea e FJP), "
      f"Censo Demográfico 2010 — {inteiro(G['n_municipios'])} municípios", "capa_txt"),
    P("<b>Ferramenta:</b> Python (pandas, SciPy, statsmodels, scikit-learn, matplotlib, seaborn)", "capa_txt"),
    Spacer(1, 1.2 * cm),
    P("<b>Integrante</b>" if len(INTEGRANTES) == 1 else "<b>Integrantes</b>", "capa_txt"),
]
H += [P(f"{nome} — {rm}", "capa_txt") for nome, rm in INTEGRANTES]
H += [Spacer(1, 1.2 * cm), P(DATA_RELATORIO, "capa_txt"), PageBreak()]

# ---- 1. Sumário executivo ---------------------------------------------------
H += [P("1. Sumário executivo", "h1")]
H += [P(
    "Este relatório investiga por que a mortalidade infantil é tão desigual entre os municípios brasileiros "
    "e o quanto dessa desigualdade está associada a três fatores sobre os quais a gestão pública pode atuar: "
    "saneamento domiciliar, educação e renda. O objetivo é apoiar a decisão de <b>onde agir primeiro</b>, "
    f"com base em dados reais do Atlas do Desenvolvimento Humano no Brasil para os {inteiro(G['n_municipios'])} "
    "municípios existentes no Censo 2010."
)]
H += [P("<b>Principais resultados</b>")]
H += itens([
    f"<b>A meta não chegou a todos.</b> {inteiro(G['n_acima_meta'])} municípios ({br(G['pct_acima_meta'], 1)}%) tinham "
    f"mortalidade infantil acima da meta de {META} óbitos por mil nascidos vivos. No Nordeste eram "
    f"{br(REG['Nordeste']['pct_acima_meta'], 1)}% dos municípios; no Sul, {br(REG['Sul']['pct_acima_meta'], 1)}%.",
    f"<b>O campo está em desvantagem.</b> Nos municípios predominantemente rurais, {br(RUR['pct_acima_meta'], 1)}% "
    f"estavam acima da meta, contra {br(URB['pct_acima_meta'], 1)}% nos predominantemente urbanos. Testes de hipóteses "
    f"com amostras de 20 e 25 municípios confirmaram a diferença em relação à média nacional "
    f"(z = {br(TA['z_calc'])} e z = {br(TB['z_calc'])}).",
    f"<b>Saneamento domiciliar e mortalidade infantil andam juntos.</b> A correlação é forte e negativa "
    f"(r = {br(R4['r'], 3)}); sozinho, o saneamento explica {br(100 * R4['r2'], 1)}% da variação entre municípios. "
    f"Cada 10 pontos percentuais a mais de cobertura correspondem, em média, a {br(abs(10 * R4['b1']), 1)} óbitos "
    "a menos por mil.",
    f"<b>Entre os três fatores, a educação é o de maior peso.</b> Com saneamento, analfabetismo adulto e renda juntos, o modelo "
    f"explica {br(100 * R5['r2'], 1)}% da variação. O analfabetismo tem o maior coeficiente padronizado "
    f"({br(BETA['taxa_analfabetismo'], 2, sinal=True)}), à frente de saneamento "
    f"({br(BETA['pct_banheiro_agua'], 2, sinal=True)}) e renda ({br(BETA['renda_per_capita'], 2, sinal=True)}).",
    f"<b>É possível fazer triagem com três indicadores.</b> A regressão logística classificou corretamente "
    f"{br(100 * R6['acuracia'], 1)}% de {inteiro(N_TESTE)} municípios que não participaram do ajuste e identificou "
    f"{br(100 * R6['sensibilidade'], 1)}% dos que estavam acima da meta.",
])
H += [P(
    "<b>Recomendação central.</b> Priorizar municípios predominantemente rurais, sobretudo do Norte e do Nordeste, "
    "que combinam baixa cobertura de saneamento domiciliar e alto analfabetismo adulto, com ações integradas "
    "(e não apenas obras de saneamento). O classificador pode ser usado como ferramenta de triagem. As conclusões "
    "descrevem associações observadas em 2010 e não provam relações de causa e efeito; as limitações estão na seção 7."
)]

# ---- 2. Contexto ------------------------------------------------------------
H += [P("2. Contexto e problema", "h1")]
H += [P(
    "O desafio CitizenTech propõe usar dados e tecnologia para enfrentar problemas concretos de cidades, do campo "
    "e de comunidades. O tema escolhido é a <b>mortalidade infantil</b> (óbitos de menores de um ano por mil nascidos vivos) "
    "porque ela é amplamente usada como indicador das condições de vida de uma população, por estar ligada ao "
    "acesso a água, instalações sanitárias, informação e renda. O tema dialoga diretamente com os "
    "Objetivos de Desenvolvimento Sustentável 3 (saúde e bem-estar) e 6 (água potável e saneamento)."
)]
H += [P(
    f"Nos Objetivos de Desenvolvimento do Milênio, a meta brasileira para a mortalidade infantil era de {META} óbitos "
    "por mil nascidos vivos até 2015, e o país a alcançou na média nacional em 2011 (Ipea; SPI, 2014). "
    "Uma média nacional, porém, esconde realidades locais muito diferentes. É nessa escala, a do município, "
    "que as decisões de investimento são tomadas e que este relatório trabalha."
)]
H += [P("<b>Perguntas de análise</b>")]
H += itens([
    "A mortalidade infantil dos municípios predominantemente urbanos e dos predominantemente rurais difere da "
    "média nacional?",
    "Quanto da variação da mortalidade infantil entre municípios está associado ao saneamento domiciliar, "
    "à educação e à renda?",
    "Com esses três indicadores, é possível classificar os municípios que estão acima da meta, de modo a apoiar "
    "a priorização de ações?",
])

# ---- 3. Dados ---------------------------------------------------------------
H += [P("3. Base de dados", "h1")]
H += [P("3.1 Fonte e coleta", "h2")]
H += [P(
    "A base é o <b>Atlas do Desenvolvimento Humano no Brasil</b>, elaborado pelo PNUD, pelo Ipea e pela Fundação "
    "João Pinheiro a partir dos Censos Demográficos do IBGE (endereço original: http://www.atlasbrasil.org.br/). "
    "Trata-se de dados reais e públicos; nenhum registro foi gerado artificialmente. O arquivo utilizado é a base "
    "municipal completa do Atlas (16.695 linhas = 5.565 municípios em 1991, 2000 e 2010; 125 colunas), obtida da "
    "cópia integral redistribuída pela Associação Brasileira de Jurimetria no pacote abjData "
    "(https://github.com/abjur/abjData) e convertida para .csv sem alteração de conteúdo. A coleta está "
    "documentada no script <i>00_obter_base_bruta.py</i>."
)]
H += [P("3.2 Preparação dos dados", "h2")]
H += [P(
    "Todas as etapas abaixo são executadas pelo script <i>01_preparacao_base.py</i> e podem ser reproduzidas "
    "a partir da base bruta incluída no repositório:"
)]
H += itens([
    "filtro do ano de 2010, o censo mais recente disponível no arquivo;",
    "seleção das variáveis ligadas ao problema e renomeação para nomes autoexplicativos;",
    "criação de variáveis derivadas: região, sigla da UF, percentual de população urbana, perfil urbano/rural "
    f"e indicador binário de mortalidade infantil acima da meta de {META};",
    "padronização dos nomes dos municípios em letras maiúsculas;",
    f"verificações de qualidade: {inteiro(G['n_municipios'])} municípios, nenhum valor ausente, nenhum município "
    "duplicado e percentuais dentro da faixa de 0 a 100. Nenhum registro foi excluído.",
])
H += [tabela([
    ["Variável", "Papel", "Descrição"],
    ["mort_infantil", "Resposta (Y)", "Crianças que não deverão sobreviver ao primeiro ano de vida, em cada 1.000 nascidas vivas."],
    ["pct_banheiro_agua", "Explicativa", "% da população em domicílios com banheiro exclusivo e água encanada em pelo menos um cômodo (saneamento domiciliar)."],
    ["taxa_analfabetismo", "Explicativa", "% de pessoas de 18 anos ou mais que não sabem ler nem escrever um bilhete simples."],
    ["renda_per_capita", "Explicativa", "Renda domiciliar per capita média mensal, em reais de agosto de 2010."],
    ["alta_mortalidade", "Resposta binária", f"1 se mort_infantil &gt; {META} (acima da meta); 0 caso contrário."],
    ["perfil", "Estratificação", "Predominantemente urbano (≥ 80% da população em área urbana), predominantemente rural (&lt; 50%) ou intermediário. Critério operacional adotado neste trabalho."],
], [3.4, 2.9, 10.7], "Variáveis utilizadas nas análises.")]

H += [P("3.3 Estatísticas descritivas", "h2")]
linhas_desc = [["Variável", "Média", "Mediana", "Desvio padrão", "Mínimo", "Máximo", "Assimetria"]]
for v in VARS:
    d = D[v]
    linhas_desc.append([CURTO[v] + {"mort_infantil": " (por mil)", "pct_banheiro_agua": " (%)",
                                    "taxa_analfabetismo": " (%)", "renda_per_capita": " (R$)"}[v],
                        br(d["média"]), br(d["mediana"]), br(d["desvio padrão (amostral)"]),
                        br(d["mínimo"]), br(d["máximo"]), br(d["assimetria"])])
H += [tabela(linhas_desc, [4.4, 2.0, 2.0, 2.5, 2.0, 2.2, 2.1],
             f"Estatísticas descritivas das variáveis quantitativas (n = {inteiro(G['n_municipios'])} municípios).")]

H += [P(
    f"A mortalidade infantil média dos municípios é de {br(D['mort_infantil']['média'])} óbitos por mil, acima da "
    f"mediana ({br(D['mort_infantil']['mediana'])}): a distribuição é assimétrica à direita. As Tabelas 2 e 3 "
    "antecipam o padrão que as análises quantificam: os recortes de maior mortalidade (Nordeste, Norte e "
    "municípios rurais) têm menor cobertura de saneamento domiciliar, mais analfabetismo e menor renda."
)]
linhas_reg = [["Recorte", "Municípios", "Mortalidade infantil média", "% acima da meta", "Saneamento médio (%)",
               "Analfabetismo médio (%)", "Renda média (R$)"]]
for nome in ["Nordeste", "Norte", "Centro-Oeste", "Sudeste", "Sul"]:
    g = REG[nome]
    linhas_reg.append([nome, inteiro(g["municipios"]), br(g["mort_infantil_media"], 1), br(g["pct_acima_meta"], 1),
                       br(g["banheiro_agua_medio"], 1), br(g["analfabetismo_medio"], 1), br(g["renda_media"], 0)])
for nome in ["Predominantemente urbano", "Intermediário", "Predominantemente rural"]:
    g = PERF[nome]
    linhas_reg.append([nome, inteiro(g["municipios"]), br(g["mort_infantil_media"], 1), br(g["pct_acima_meta"], 1),
                       br(g["banheiro_agua_medio"], 1), br(g["analfabetismo_medio"], 1), br(g["renda_media"], 0)])
H += [tabela(linhas_reg, [3.9, 2.1, 2.35, 1.8, 2.4, 2.75, 1.7],
             "Indicadores médios dos municípios por região e por perfil urbano/rural.")]
H += [figura("fig01_mortalidade_por_regiao.png", 7.8,
             "Mortalidade infantil média dos municípios por região, comparada à meta.")]

# ---- 4. Procedimentos -------------------------------------------------------
H += [P("4. Procedimentos adotados", "h1")]
H += [P(
    "As análises foram feitas em Python, no notebook <i>02_analise_estatistica.ipynb</i>, que preserva todas as "
    "saídas. Sorteios e divisão entre treino e teste usam semente fixa (42): a execução do código reproduz "
    "exatamente os números deste relatório."
)]
H += tabela([
    ["Etapa", "Técnica", "Como foi aplicada"],
    ["Distribuição Normal", "Probabilidades pela curva Normal", "Mortalidade infantil assumida Normal, com média e desvio padrão populacionais; cálculo de P(X &lt; média) e P(X &gt; mediana)."],
    ["Testes de hipóteses", "Teste Z unilateral para a média (σ conhecido)", "Referências: média e desvio padrão populacionais de todos os municípios. Amostras aleatórias de 20 municípios urbanos (α = 6%) e de 25 rurais (α = 9%)."],
    ["Análise bivariada", "Covariância, correlação de Pearson e regressão linear simples", "Mortalidade infantil em função do saneamento domiciliar; adequação pelo R² e pelo teste F."],
    ["Análise multivariada", "Regressão linear múltipla", "Mortalidade infantil em função de saneamento, analfabetismo e renda; R², teste F, VIF, teste de Breusch-Pagan e erros padrão robustos."],
    ["Classificação", "Regressão logística binária", "Resposta: acima ou não da meta. Ajuste em 70% dos municípios e avaliação nos 30% restantes; matriz de confusão e acurácia."],
], [2.7, 5.3, 9.0], "Técnicas estatísticas utilizadas.", pode_dividir=True)

# ---- 5. Resultados ----------------------------------------------------------
H += [P("5. Resultados e interpretações", "h1")]

# 5.1
H += [P("5.1 Distribuição Normal de Probabilidade", "h2")]
H += [P(
    "Variável aleatória: X = mortalidade infantil do município. Conforme a proposta da avaliação, assume-se "
    f"X ~ Normal(μ = {br(R2['mu'])}; σ = {br(R2['sigma'])}), com parâmetros iguais à média e ao desvio padrão "
    "populacionais dos registros. Os eventos foram classificados pela escala: impossível (P = 0), improvável "
    "(0 &lt; P &lt; 0,5), tão provável quanto improvável (P = 0,5), provável (0,5 &lt; P &lt; 1) e certo (P = 1)."
)]
H += [tabela([
    ["Evento", "Padronização (z)", "Probabilidade (modelo Normal)", "Classificação", "Proporção observada na base"],
    [f"a) X &lt; média ({br(R2['mu'])})", br(R2["z_a"]), f"{br(R2['p_a'], 4)} ({br(100 * R2['p_a'], 2)}%)",
     R2["classe_a"].capitalize(), f"{br(100 * R2['prop_empirica_a'], 1)}%"],
    [f"b) X &gt; mediana ({br(R2['mediana'])})", br(R2["z_b"], 4), f"{br(R2['p_b'], 4)} ({br(100 * R2['p_b'], 2)}%)",
     R2["classe_b"].capitalize(), f"{br(100 * R2['prop_empirica_b'], 1)}%"],
], [3.7, 2.9, 3.4, 3.9, 3.1], "Probabilidades calculadas pela distribuição Normal.")]
H += [figura("fig02_distribuicao_normal.png", 15.5,
             "Curva Normal assumida, áreas correspondentes às probabilidades e histograma dos dados observados.")]
H += [P(
    f"<b>Interpretação.</b> (a) Na curva Normal a média divide a área em duas metades, portanto "
    f"P(X &lt; média) = {br(100 * R2['p_a'], 0)}%: um município sorteado ao acaso tem a mesma chance de estar abaixo "
    f"ou acima de {br(R2['mu'])} óbitos por mil. (b) Como a mediana ({br(R2['mediana'])}) está "
    f"{br(abs(R2['z_b']))} desvio padrão abaixo da média, a área à sua direita supera a metade: "
    f"P(X &gt; mediana) = {br(100 * R2['p_b'], 1)}%, um evento provável."
)]
H += [P(
    f"<b>Ressalva.</b> Na base real, {br(100 * R2['prop_empirica_a'], 1)}% dos municípios estão abaixo da média e "
    f"{br(100 * R2['prop_empirica_b'], 1)}% acima da mediana. As diferenças em relação ao modelo decorrem da "
    "assimetria à direita visível no histograma: a hipótese de normalidade é uma simplificação, e as "
    "probabilidades acima devem ser lidas como aproximações."
)]

# 5.2
H += [P("5.2 Testes de hipóteses para a média", "h2")]
H += [P(
    f"Média populacional de referência: μ<sub>0</sub> = {br(R3['mu0'])} (todos os municípios). Desvio padrão de "
    f"referência: σ = {br(R3['sigma'])} (desvio padrão populacional dos dados). Como σ é conhecido e a variável "
    "é assumida Normal, usou-se o teste Z: z = (média amostral − μ<sub>0</sub>) / (σ / √n). Para ligar o teste ao "
    "problema, as amostras foram sorteadas dentro de dois grupos de interesse: municípios predominantemente "
    "urbanos (item a) e predominantemente rurais (item b)."
)]
H += [tabela([
    ["", "a) Municípios urbanos", "b) Municípios rurais"],
    ["Hipótese nula (H<sub>0</sub>)", "μ = μ<sub>0</sub> (a média do grupo não é menor que a referência)",
     "μ = μ<sub>0</sub> (a média do grupo não é maior que a referência)"],
    ["Hipótese alternativa (H<sub>1</sub>)", "μ &lt; μ<sub>0</sub> (unilateral à esquerda)", "μ &gt; μ<sub>0</sub> (unilateral à direita)"],
    ["Nível de significância (α)", "6%", "9%"],
    ["Tamanho da amostra (n)", str(TA["n"]), str(TB["n"])],
    ["Média amostral", br(TA["media_amostral"]), br(TB["media_amostral"])],
    ["Erro padrão (σ / √n)", br(TA["erro_padrao"], 4), br(TB["erro_padrao"], 4)],
    ["z calculado", br(TA["z_calc"]), br(TB["z_calc"])],
    ["z crítico", br(TA["z_crit"]), br(TB["z_crit"])],
    ["p-valor", fmt_p(TA["p_valor"], False), fmt_p(TB["p_valor"], False)],
    ["Decisão", decisao_a, decisao_b],
    ["Rejeições em 10.000 novos sorteios", f"{br(100 * TA['prop_rejeicoes'], 1)}%", f"{br(100 * TB['prop_rejeicoes'], 1)}%"],
    ["Média real do grupo (todos os municípios)", f"{br(TA['media_real_grupo'])} (n = {inteiro(TA['n_grupo'])})",
     f"{br(TB['media_real_grupo'])} (n = {inteiro(TB['n_grupo'])})"],
], [5.6, 5.7, 5.7], "Testes Z unilaterais para a média da mortalidade infantil.", cabecalho_esquerda=True)]
H += [figura("fig03_testes_hipoteses.png", 15.5,
             "Regiões de rejeição, valores críticos e estatísticas calculadas nos dois testes.")]
H += [P(
    f"<b>Interpretação.</b> (a) A amostra de {TA['n']} municípios urbanos teve média de {br(TA['media_amostral'])}, "
    f"abaixo da referência. O z calculado ({br(TA['z_calc'])}) está à esquerda do z crítico ({br(TA['z_crit'])}) "
    f"e o p-valor ({fmt_p(TA['p_valor'], False)}) é menor que α = 0,06: "
    + ("rejeita-se H<sub>0</sub>. Há evidência, ao nível de 6%, de que a mortalidade infantil média dos municípios "
       "predominantemente urbanos é menor do que a referência nacional. " if TA["rejeita_h0"] else
       "não se rejeita H<sub>0</sub>. A amostra não traz evidência suficiente, ao nível de 6%, de que a média dos "
       "municípios predominantemente urbanos seja menor do que a referência nacional. ")
    + f"(b) A amostra de {TB['n']} municípios rurais teve média de {br(TB['media_amostral'])}; o z calculado "
    f"({br(TB['z_calc'])}) está à direita do z crítico ({br(TB['z_crit'])}) e o p-valor é {fmt_p(TB['p_valor'], False)}: "
    + ("rejeita-se H<sub>0</sub>. Há evidência, ao nível de 9%, de que a mortalidade infantil média dos municípios "
       "predominantemente rurais é maior do que a referência nacional." if TB["rejeita_h0"] else
       "não se rejeita H<sub>0</sub>. A amostra não traz evidência suficiente, ao nível de 9%, de que a média dos "
       "municípios predominantemente rurais seja maior do que a referência nacional.")
)]
H += [P(
    "<b>Robustez.</b> Como a decisão de um teste depende da amostra sorteada, o sorteio foi repetido 10.000 vezes: "
    f"H<sub>0</sub> seria rejeitada em {br(100 * TA['prop_rejeicoes'], 1)}% das amostras urbanas e em "
    f"{br(100 * TB['prop_rejeicoes'], 1)}% das rurais. As decisões se repetem na maioria dos sorteios, mas amostras "
    "tão pequenas ainda deixam uma chance relevante de não detectar a diferença. As médias reais dos dois grupos "
    "(última linha da Tabela 6) são coerentes com as decisões obtidas."
)]

# 5.3
H += [P("5.3 Análise bivariada: saneamento domiciliar e mortalidade infantil", "h2")]
H += [P(
    "X = percentual da população em domicílios com banheiro e água encanada; Y = mortalidade infantil."
)]
H += [figuras_lado_a_lado("fig04_dispersao_simples.png", "fig05_correlacao_bivariada.png", 9.2, 7.0,
                          "Gráfico de dispersão (esquerda) e gráfico de correlação linear de Pearson (direita).")]
H += [P(
    "<b>Dispersão.</b> A nuvem de pontos é descendente: quanto maior a cobertura de saneamento domiciliar, menor "
    f"a mortalidade infantil. Nos {inteiro(FAIXAS[0]['municipios'])} municípios com até 40% de cobertura a média é "
    f"de {br(FAIXAS[0]['media'], 1)} óbitos por mil; nos {inteiro(FAIXAS[-1]['municipios'])} com mais de 95%, de "
    f"{br(FAIXAS[-1]['media'], 1)}. A relação não é perfeitamente reta (a queda é mais lenta abaixo de 60% de "
    "cobertura) e a dispersão vertical é grande, sinal de que o saneamento não explica tudo sozinho."
)]
H += [P(
    f"<b>Covariância e correlação.</b> A covariância é {br(R4['covariancia'])}: o sinal negativo indica que as "
    "variáveis caminham em sentidos opostos, mas a magnitude depende das unidades e não mede intensidade. "
    f"A correlação de Pearson, r = {br(R4['r'], 3)}, indica associação linear negativa e {R4['forca']}, "
    f"estatisticamente diferente de zero (p {fmt_p(R4['p_r'])}). No gráfico de correlação, a célula que cruza as "
    "duas variáveis aparece em azul, cor das correlações negativas."
)]
H += [figura("fig06_regressao_simples.png", 10.0, "Reta de regressão linear simples sobre o gráfico de dispersão.")]
H += [P(f"mortalidade infantil = {br(R4['b0'])} − {br(abs(R4['b1']), 3)} × (% com banheiro e água encanada)", "eq")]
H += [tabela([
    ["Medida", "Valor", "Leitura"],
    ["Inclinação (b<sub>1</sub>)", br(R4["b1"], 3), f"Cada 1 ponto percentual a mais de cobertura está associado a {br(abs(R4['b1']), 3)} óbito a menos por mil."],
    ["Intercepto (b<sub>0</sub>)", br(R4["b0"]), f"Valor previsto para 0% de cobertura; é uma extrapolação (mínimo observado: {br(R4['x_min'], 1)}%)."],
    ["R²", br(R4["r2"], 3), f"O saneamento domiciliar explica {br(100 * R4['r2'], 1)}% da variação da mortalidade infantil."],
    [f"Teste F ({R4['gl_modelo']}; {inteiro(R4['gl_residuo'])})", f"F = {br(R4['f'], 1)}; p {fmt_p(R4['p_f'])}", "Rejeita-se a hipótese de que a inclinação é zero: o modelo é significativo."],
    [f"Previsão para {br(R4['x_novo'], 0)}% de cobertura", f"{br(R4['previsao'], 1)} por mil", f"Intervalo de previsão de 95%: {br(R4['ip_inf'], 1)} a {br(R4['ip_sup'], 1)}. Para {br(R4['x_comparacao'], 0)}% de cobertura, a previsão é {br(R4['previsao_comparacao'], 1)}."],
], [4.2, 3.7, 9.1], "Regressão linear simples: equação, adequação do modelo e previsão.")]
H += [P(
    f"<b>Interpretação.</b> O modelo é estatisticamente significativo e tem poder explicativo relevante, mas "
    f"{br(100 * (1 - R4['r2']), 1)}% da variação ficam sem explicação. Com mais de 5 mil observações quase qualquer "
    "associação é significativa; por isso o R² e o tamanho do efeito importam mais do que o p-valor. Um município "
    f"com {br(R4['x_novo'], 0)}% de cobertura tem mortalidade prevista de {br(R4['previsao'], 1)} por mil, acima da "
    f"meta de {META}; o intervalo de previsão é largo, isto é, o modelo indica o nível médio esperado e não o "
    "valor exato de um município."
)]

# 5.4
H += [P("5.4 Regressão linear múltipla: saneamento, educação e renda", "h2")]
H += [P(
    "Y = mortalidade infantil; X<sub>1</sub> = saneamento domiciliar; X<sub>2</sub> = analfabetismo adulto; "
    "X<sub>3</sub> = renda per capita. A pergunta é quanto cada fator contribui quando os três são considerados "
    "ao mesmo tempo."
)]
H += [figura("fig07_dispersao_multipla.png", 14.2, "Matriz de gráficos de dispersão entre as quatro variáveis.")]
H += [P(
    "<b>Dispersões.</b> A mortalidade infantil cai com o saneamento e com a renda e sobe com o analfabetismo, que "
    "apresenta a relação mais próxima de uma reta. A relação com a renda é curva: a queda é forte entre os "
    "municípios mais pobres e bem mais lenta nas faixas de renda mais altas. As três variáveis explicativas "
    "também se relacionam fortemente entre si."
)]
cov = R5["cov"]
linhas_cov = [[""] + [CURTO[v] for v in VARS]]
for v in VARS:
    linhas_cov.append([CURTO[v]] + [br(cov[c][v], 1) for c in VARS])
H += [tabela(linhas_cov, [3.6, 3.2, 3.2, 3.2, 3.2], "Matriz de covariância (amostral).", cabecalho_esquerda=True)]
corr = R5["corr"]
linhas_corr = [[""] + [CURTO[v] for v in VARS]]
for v in VARS:
    linhas_corr.append([CURTO[v]] + [br(corr[c][v], 3) for c in VARS])
H += [tabela(linhas_corr, [3.6, 3.2, 3.2, 3.2, 3.2], "Matriz de correlação linear de Pearson.", cabecalho_esquerda=True)]
H += [figura("fig08_correlacao_multipla.png", 9.4, "Gráfico de correlação linear de Pearson entre as quatro variáveis.")]
H += [P(
    "<b>Covariâncias e correlações.</b> Os sinais das covariâncias mostram o sentido das relações, mas as "
    "magnitudes não são comparáveis porque dependem das unidades (a variância da renda é enorme apenas por ser "
    f"medida em reais). Nas correlações, a mortalidade infantil associa-se mais fortemente ao analfabetismo "
    f"(r = {br(corr['mort_infantil']['taxa_analfabetismo'], 3)}), seguido de renda "
    f"(r = {br(corr['mort_infantil']['renda_per_capita'], 3)}) e saneamento "
    f"(r = {br(corr['mort_infantil']['pct_banheiro_agua'], 3)}). As explicativas também são fortemente "
    f"correlacionadas entre si (de {br(abs(corr['pct_banheiro_agua']['renda_per_capita']), 2)} a "
    f"{br(abs(corr['taxa_analfabetismo']['renda_per_capita']), 2)} em módulo), o que exige analisá-las em conjunto."
)]
H += [P(
    f"mortalidade infantil = {br(COEF['const'])} − {br(abs(COEF['pct_banheiro_agua']), 4)} × saneamento "
    f"+ {br(COEF['taxa_analfabetismo'], 4)} × analfabetismo − {br(abs(COEF['renda_per_capita']), 5)} × renda", "eq")]
linhas_coef = [["Variável", "Coeficiente", "Coeficiente padronizado", "p-valor (teste t)", "p-valor robusto (HC3)", "VIF"]]
for v in ["pct_banheiro_agua", "taxa_analfabetismo", "renda_per_capita"]:
    linhas_coef.append([ROTULO[v], br(COEF[v], 5 if v == "renda_per_capita" else 4), br(BETA[v], 3, sinal=True),
                        fmt_p(R5["p_coef"][v], False), fmt_p(R5["p_robustos"][v], False), br(R5["vif"][v])])
linhas_coef.append(["Intercepto", br(COEF["const"], 4), "—", fmt_p(R5["p_coef"]["const"], False),
                    fmt_p(R5["p_robustos"]["const"], False), "—"])
H += [tabela(linhas_coef, [6.2, 2.2, 2.6, 2.2, 2.3, 1.5], "Coeficientes da regressão linear múltipla.")]
H += [tabela([
    ["Medida", "Valor", "Leitura"],
    ["R²", br(R5["r2"], 3), f"Os três fatores explicam em conjunto {br(100 * R5['r2'], 1)}% da variação da mortalidade infantil (modelo simples: {br(100 * R4['r2'], 1)}%)."],
    ["R² ajustado", br(R5["r2_ajustado"], 3), "Praticamente igual ao R²: o ganho não é efeito do número de variáveis."],
    [f"Teste F ({R5['gl_modelo']}; {inteiro(R5['gl_residuo'])})", f"F = {br(R5['f'], 1)}; p {fmt_p(R5['p_f'])}", "Rejeita-se a hipótese de que todos os coeficientes são zero: o modelo é significativo."],
    ["Desvio padrão dos resíduos", f"{br(R5['dp_residuos'])} por mil", "Erro típico das previsões do modelo."],
    ["Breusch-Pagan", f"LM = {br(R5['bp_lm'], 1)}; p {fmt_p(R5['bp_p'])}", "A variância dos resíduos não é constante (heterocedasticidade)."],
], [4.2, 3.7, 9.1], "Adequação e diagnósticos da regressão linear múltipla.")]
H += [P(
    "<b>Interpretação.</b> Mantidas as demais variáveis constantes, cada ponto percentual a mais de saneamento "
    f"domiciliar está associado a {br(abs(COEF['pct_banheiro_agua']), 3)} óbito a menos por mil; cada ponto "
    f"percentual a mais de analfabetismo adulto, a {br(COEF['taxa_analfabetismo'], 3)} óbito a mais; e cada R$ 100 "
    f"a mais de renda per capita, a {br(abs(100 * COEF['renda_per_capita']), 2)} óbito a menos. O coeficiente do "
    f"saneamento é {br(REDUCAO_SANEAMENTO, 0)}% menor do que no modelo simples ({br(R4['b1'], 3)} → "
    f"{br(COEF['pct_banheiro_agua'], 3)}): boa parte da associação atribuída ao saneamento era compartilhada com "
    "educação e renda. Pelos coeficientes padronizados, o analfabetismo é o fator de maior peso."
)]
H += [P(
    f"<b>Diagnósticos.</b> Os VIFs (de {br(min(R5['vif'].values()), 1)} a {br(max(R5['vif'].values()), 1)}) indicam "
    "multicolinearidade moderada, abaixo do nível usual de atenção (5). O teste de Breusch-Pagan aponta "
    "heterocedasticidade, visível na Figura 8: o modelo erra mais nos municípios de mortalidade mais alta. "
    "Por isso os p-valores foram recalculados com erros padrão robustos, e os três coeficientes permaneceram "
    "significativos."
)]
H += [figura("fig09_residuos_multipla.png", 10.6, "Resíduos da regressão múltipla em função dos valores ajustados.")]
ca, cb = R5["cenario_a"], R5["cenario_b"]
H += [tabela([
    ["Município hipotético", "Saneamento (%)", "Analfabetismo (%)", "Renda (R$)", "Mortalidade infantil prevista", "Intervalo de previsão (95%)"],
    ["A (carência)", br(ca["pct_banheiro_agua"], 0), br(ca["taxa_analfabetismo"], 0), br(ca["renda_per_capita"], 0),
     f"{br(R5['prev_a'], 1)} por mil", f"{br(R5['prev_a_inf'], 1)} a {br(R5['prev_a_sup'], 1)}"],
    ["B (boa cobertura)", br(cb["pct_banheiro_agua"], 0), br(cb["taxa_analfabetismo"], 0), br(cb["renda_per_capita"], 0),
     f"{br(R5['prev_b'], 1)} por mil", f"{br(R5['prev_b_inf'], 1)} a {br(R5['prev_b_sup'], 1)}"],
], [3.2, 2.4, 2.75, 1.8, 3.4, 3.2], "Previsões da regressão múltipla com as três variáveis explicativas.")]
H += [P(
    f"<b>Previsão.</b> O município A tem mortalidade prevista de {br(R5['prev_a'], 1)} por mil, acima da meta de "
    f"{META}; o município B, de {br(R5['prev_b'], 1)}, abaixo dela. A diferença de "
    f"{br(R5['prev_a'] - R5['prev_b'], 1)} óbitos por mil resume a desigualdade associada aos três fatores. "
    "As previsões descrevem o nível médio de municípios com esses perfis; não significam que alterar um "
    "indicador isoladamente produzirá esse efeito."
)]

# 5.5
H += [P("5.5 Regressão logística binária: municípios acima da meta", "h2")]
H += [P(
    f"Resposta: alta_mortalidade = 1 se a mortalidade infantil supera {META} por mil. Explicativas: saneamento "
    f"domiciliar, analfabetismo adulto e renda per capita. O modelo foi ajustado em {inteiro(R6['n_treino'])} "
    f"municípios (treino) e avaliado em {inteiro(N_TESTE)} municípios que não participaram do ajuste (teste). "
    "Sendo p a probabilidade de o município estar acima da meta:"
)]
H += [P(
    f"ln[p / (1 − p)] = {br(LOGI['const'], 4)} − {br(abs(LOGI['pct_banheiro_agua']), 4)} × saneamento "
    f"+ {br(LOGI['taxa_analfabetismo'], 4)} × analfabetismo − {br(abs(LOGI['renda_per_capita']), 5)} × renda", "eq")]
ic = R6["razao_chance_ic"]
linhas_or = [["Variável", "Coeficiente", "Razão de chances", "IC 95% da razão de chances", "p-valor"]]
for v in ["pct_banheiro_agua", "taxa_analfabetismo", "renda_per_capita"]:
    linhas_or.append([ROTULO[v], br(LOGI[v], 5 if v == "renda_per_capita" else 4), br(R6["razao_chance"][v], 4),
                      f"{br(ic[v][0], 4)} a {br(ic[v][1], 4)}", fmt_p(R6["p_coef"][v], False)])
H += [tabela(linhas_or, [6.6, 2.3, 2.6, 3.6, 1.9], "Coeficientes e razões de chances da regressão logística (ajuste no treino).")]
H += [P(
    "<b>Interpretação da equação.</b> Mantidas as demais variáveis constantes, cada ponto percentual a mais de "
    f"saneamento domiciliar multiplica a chance de o município estar acima da meta por "
    f"{br(R6['razao_chance']['pct_banheiro_agua'], 3)} (redução de "
    f"{br(100 * (1 - R6['razao_chance']['pct_banheiro_agua']), 1)}%); cada ponto percentual a mais de analfabetismo "
    f"multiplica a chance por {br(R6['razao_chance']['taxa_analfabetismo'], 3)} (aumento de "
    f"{br(100 * (R6['razao_chance']['taxa_analfabetismo'] - 1), 1)}%); e cada R$ 100 a mais de renda per capita "
    f"multiplica a chance por {br(R6['razao_chance_renda_100'], 3)} (redução de "
    f"{br(100 * (1 - R6['razao_chance_renda_100']), 1)}%). Os sinais são os mesmos da regressão linear múltipla."
)]
metricas = Table([[
    imagem("fig10_matriz_confusao.png", 7.6 * cm),
    Table([
        [Paragraph("Medida (conjunto de teste)", E["cel_hl"]), Paragraph("Valor", E["cel_h"])],
        [Paragraph("Verdadeiros positivos (VP)", E["cel"]), Paragraph(inteiro(R6["vp"]), E["cel_c"])],
        [Paragraph("Verdadeiros negativos (VN)", E["cel"]), Paragraph(inteiro(R6["vn"]), E["cel_c"])],
        [Paragraph("Falsos positivos (FP)", E["cel"]), Paragraph(inteiro(R6["fp"]), E["cel_c"])],
        [Paragraph("Falsos negativos (FN)", E["cel"]), Paragraph(inteiro(R6["fn"]), E["cel_c"])],
        [Paragraph("<b>Acurácia</b> = (VP + VN) / total", E["cel"]), Paragraph(f"<b>{br(100 * R6['acuracia'], 1)}%</b>", E["cel_c"])],
        [Paragraph("Acurácia no treino", E["cel"]), Paragraph(f"{br(100 * R6['acuracia_treino'], 1)}%", E["cel_c"])],
        [Paragraph("Acurácia de referência (classe mais frequente)", E["cel"]), Paragraph(f"{br(100 * R6['acuracia_base'], 1)}%", E["cel_c"])],
        [Paragraph("Sensibilidade = VP / (VP + FN)", E["cel"]), Paragraph(f"{br(100 * R6['sensibilidade'], 1)}%", E["cel_c"])],
        [Paragraph("Especificidade = VN / (VN + FP)", E["cel"]), Paragraph(f"{br(100 * R6['especificidade'], 1)}%", E["cel_c"])],
        [Paragraph("Precisão = VP / (VP + FP)", E["cel"]), Paragraph(f"{br(100 * R6['precisao'], 1)}%", E["cel_c"])],
    ], colWidths=[6.3 * cm, 2.1 * cm], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_FUNDO), ("LINEABOVE", (0, 0), (-1, 0), 0.9, AZUL),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, AZUL), ("LINEBELOW", (0, 1), (-1, -2), 0.3, LINHA),
        ("LINEBELOW", (0, -1), (-1, -1), 0.9, AZUL), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
    ])),
]], colWidths=[8.1 * cm, 8.9 * cm])
metricas.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
H += [KeepTogether([metricas, legenda("figura", f"Matriz de confusão e medidas de desempenho no conjunto de teste (n = {inteiro(N_TESTE)}; limiar de classificação = 0,5).")])]
H += [P(
    f"<b>Matriz de confusão e acurácia.</b> O modelo acertou {inteiro(R6['vp'] + R6['vn'])} dos {inteiro(N_TESTE)} "
    f"municípios de teste: acurácia de {br(100 * R6['acuracia'], 1)}%, bem acima dos {br(100 * R6['acuracia_base'], 1)}% "
    "que se obteriam prevendo sempre a classe mais frequente. A acurácia no treino é praticamente a mesma, sinal de "
    f"que não há sobreajuste. Dos {inteiro(R6['vp'] + R6['fn'])} municípios realmente acima da meta, "
    f"{inteiro(R6['vp'])} foram identificados e {inteiro(R6['fn'])} escaparam (falsos negativos); dos "
    f"{inteiro(R6['vn'] + R6['fp'])} dentro da meta, {inteiro(R6['fp'])} receberam alerta indevido (falsos positivos). "
    "Em uma política de priorização, o falso negativo tende a ser o erro mais custoso, pois deixa fora do radar "
    "um município em situação ruim; reduzir o limiar de classificação abaixo de 0,5 diminui esse erro, ao custo de "
    "mais falsos positivos."
)]
cl = R6["classificacoes"]
H += [tabela([
    ["Município hipotético", "Saneamento (%)", "Analfabetismo (%)", "Renda (R$)", "Probabilidade de estar acima da meta", "Classificação"],
    ["A (carência)", br(ca["pct_banheiro_agua"], 0), br(ca["taxa_analfabetismo"], 0), br(ca["renda_per_capita"], 0),
     f"{br(100 * cl['A']['probabilidade'], 1)}%", "Acima da meta (1)" if cl["A"]["classe"] == 1 else "Dentro da meta (0)"],
    ["B (boa cobertura)", br(cb["pct_banheiro_agua"], 0), br(cb["taxa_analfabetismo"], 0), br(cb["renda_per_capita"], 0),
     f"{br(100 * cl['B']['probabilidade'], 1)}%", "Acima da meta (1)" if cl["B"]["classe"] == 1 else "Dentro da meta (0)"],
], [3.2, 2.4, 2.75, 1.8, 3.6, 3.0], "Classificação de dois municípios hipotéticos com as três variáveis explicativas.")]
H += [P(
    f"<b>Classificação.</b> O município A tem probabilidade estimada de {br(100 * cl['A']['probabilidade'], 1)}% de "
    "estar acima da meta e é classificado como de alta mortalidade; o município B, de "
    f"{br(100 * cl['B']['probabilidade'], 1)}%, é classificado como dentro da meta. As classificações são coerentes "
    f"com as previsões da regressão múltipla para os mesmos perfis ({br(R5['prev_a'], 1)} e {br(R5['prev_b'], 1)} "
    "óbitos por mil)."
)]

# ---- 6. Insights ------------------------------------------------------------
H += [tabela([
    ["Evidência", "O que significa para a decisão"],
    [f"{br(G['pct_acima_meta'], 1)}% dos municípios acima da meta; {br(REG['Nordeste']['pct_acima_meta'], 1)}% no Nordeste e "
     f"{br(REG['Norte']['pct_acima_meta'], 1)}% no Norte, contra {br(REG['Sul']['pct_acima_meta'], 1)}% no Sul.",
     "O problema é territorialmente concentrado. Os dados indicam que o esforço deve se concentrar no Norte e no Nordeste, e não ser distribuído de forma uniforme."],
    [f"Municípios rurais: média de {br(RUR['mort_infantil_media'], 1)} por mil e {br(RUR['pct_acima_meta'], 1)}% acima da meta; "
     f"urbanos: {br(URB['mort_infantil_media'], 1)} e {br(URB['pct_acima_meta'], 1)}%. Diferenças confirmadas pelos testes Z.",
     "O perfil urbano/rural deve entrar como critério de priorização: a situação dos municípios predominantemente rurais é sistematicamente pior do que a dos urbanos."],
    [f"Saneamento domiciliar: r = {br(R4['r'], 3)} e R² = {br(R4['r2'], 3)}. {inteiro(N_BAIXA_COBERTURA)} municípios tinham até 60% "
     f"de cobertura, com mortalidade média de {br(FAIXAS[1]['media'], 1)} a {br(FAIXAS[0]['media'], 1)} por mil.",
     "A cobertura de banheiro e água encanada é um bom critério inicial de priorização: é simples de medir e fortemente associada ao desfecho."],
    [f"No modelo conjunto (R² = {br(R5['r2'], 3)}), o coeficiente do saneamento cai {br(REDUCAO_SANEAMENTO, 0)}% e o analfabetismo adulto "
     f"tem o maior peso padronizado ({br(BETA['taxa_analfabetismo'], 2, sinal=True)}).",
     "Saneamento isolado tende a entregar menos do que a análise simples sugere. Os dados favorecem ações integradas, que combinem infraestrutura com educação e informação às famílias."],
    [f"Classificador com {br(100 * R6['acuracia'], 1)}% de acurácia e {br(100 * R6['sensibilidade'], 1)}% de sensibilidade em municípios fora do ajuste.",
     "Três indicadores socioeconômicos bastam para uma triagem inicial de municípios prioritários, útil quando o dado de mortalidade está defasado ou é pouco confiável."],
], [8.3, 8.7], "Síntese das evidências e implicações.", antes=[P("6. Insights para a tomada de decisão", "h1")])]
H += [P("<b>Recomendações</b>")]
H += itens([
    "<b>Priorizar por território e perfil:</b> começar pelos municípios predominantemente rurais do Norte e do "
    "Nordeste com baixa cobertura de saneamento domiciliar e alto analfabetismo adulto.",
    "<b>Planejar ações integradas:</b> associar a expansão de banheiro e água encanada a ações de educação e de "
    "informação em saúde, em vez de tratar o saneamento como solução única.",
    "<b>Usar o classificador como triagem, não como veredito:</b> a lista gerada pelo modelo deve ser validada "
    "com dados locais; para não deixar municípios críticos de fora, recomenda-se um limiar de classificação "
    "menor que 0,5.",
    "<b>Atualizar e ampliar os dados antes de decidir:</b> repetir a análise com informações mais recentes e "
    "incluir indicadores de acesso a serviços de saúde, ausentes desta base.",
])
H += [P(
    "No contexto do CitizenTech, esses resultados podem alimentar um painel público de priorização, em que cada "
    "município é apresentado com seus três indicadores, a mortalidade infantil prevista e a probabilidade de "
    "estar acima da meta, tornando transparente para a comunidade o critério de escolha das áreas atendidas."
)]

# ---- 7. Limitações ----------------------------------------------------------
H += [P("7. Limitações das análises", "h1")]
H += itens([
    "<b>Dados de 2010.</b> A base retrata o Censo 2010, o ano mais recente do arquivo utilizado. A situação "
    "atual dos municípios pode ser diferente, e os resultados não devem ser lidos como retrato do presente.",
    "<b>Mortalidade infantil estimada.</b> No Atlas, a mortalidade infantil municipal é estimada por métodos "
    "demográficos indiretos a partir do Censo, e não pela contagem direta de óbitos registrados; em municípios "
    "pequenos a estimativa é menos precisa, e parte da associação observada pode refletir o próprio método "
    "de estimação.",
    "<b>Associação não é causalidade.</b> Os dados são observacionais e de um único ano. Saneamento, educação e "
    "renda variam juntos e podem refletir fatores não incluídos, como o acesso a serviços de saúde.",
    "<b>Dados agregados.</b> As conclusões valem para municípios, não para famílias ou pessoas. Cada município "
    "tem o mesmo peso, independentemente da sua população.",
    "<b>Alcance do indicador de saneamento.</b> A variável mede a presença de banheiro exclusivo e de água "
    "encanada no domicílio; não informa sobre rede coletora, tratamento de esgoto ou qualidade da água.",
    "<b>Hipótese de normalidade.</b> As seções 5.1 e 5.2 assumem distribuição Normal, mas a mortalidade infantil "
    "é assimétrica à direita; as probabilidades calculadas são aproximações.",
    "<b>Linearidade e variância dos resíduos.</b> As relações com saneamento e renda são curvas em parte da "
    "faixa, e os resíduos têm variância não constante; os modelos lineares resumem a tendência média.",
    "<b>Dependência espacial.</b> Municípios vizinhos se parecem, o que viola a independência das observações e "
    "tende a tornar os p-valores otimistas.",
    "<b>Corte binário e critérios adotados.</b> Classificar como acima ou abaixo da meta descarta informação, e "
    "os limites de 80% e 50% usados para definir municípios urbanos e rurais são um critério operacional; "
    "outros cortes podem alterar os números.",
])

# ---- 8. Conclusão -----------------------------------------------------------
H += [P("8. Conclusão", "h1")]
H += [P(
    f"Em 2010, a maioria dos municípios brasileiros ({br(G['pct_acima_meta'], 1)}%) ainda tinha mortalidade infantil "
    f"acima da meta de {META} óbitos por mil nascidos vivos, com forte concentração no Norte, no Nordeste e nos "
    "municípios predominantemente rurais. Os testes de hipóteses confirmaram que as médias dos municípios urbanos "
    "e rurais diferem da referência nacional, em sentidos opostos."
)]
H += [P(
    f"O saneamento domiciliar está fortemente associado à mortalidade infantil e, sozinho, explica "
    f"{br(100 * R4['r2'], 1)}% da sua variação. Quando educação e renda entram no modelo, a explicação sobe para "
    f"{br(100 * R5['r2'], 1)}% e o analfabetismo adulto passa a ser o fator de maior peso. A regressão logística "
    f"mostrou que esses três indicadores permitem classificar corretamente {br(100 * R6['acuracia'], 1)}% dos "
    "municípios quanto ao cumprimento da meta."
)]
H += [P(
    "Para o problema proposto, a principal mensagem é que a priorização pode ser feita com dados públicos e "
    "critérios transparentes, e que ela deve combinar território (campo, Norte e Nordeste) e ações integradas de "
    "infraestrutura e educação. Essas conclusões descrevem associações entre municípios em 2010; antes de orientar "
    "investimentos, devem ser atualizadas com dados recentes e complementadas com indicadores de saúde."
)]

# ---- Referências ------------------------------------------------------------
H += [PageBreak(), P("Referências", "h1")]
for texto in [
    "ASSOCIAÇÃO BRASILEIRA DE JURIMETRIA. <b>abjData</b>: databases used routinely by the Brazilian Jurimetrics "
    "Association. Disponível em: https://github.com/abjur/abjData. Acesso em: 14 nov. 2026.",
    "INSTITUTO DE PESQUISA ECONÔMICA APLICADA; SECRETARIA DE PLANEJAMENTO E INVESTIMENTOS ESTRATÉGICOS. "
    "<b>Objetivos de Desenvolvimento do Milênio</b>: relatório nacional de acompanhamento. Brasília: Ipea, 2014.",
    "PROGRAMA DAS NAÇÕES UNIDAS PARA O DESENVOLVIMENTO; INSTITUTO DE PESQUISA ECONÔMICA APLICADA; FUNDAÇÃO JOÃO "
    "PINHEIRO. <b>Atlas do Desenvolvimento Humano no Brasil</b>. Disponível em: http://www.atlasbrasil.org.br/. "
    "Acesso em: 14 nov. 2026.",
    "PROGRAMA DAS NAÇÕES UNIDAS PARA O DESENVOLVIMENTO; INSTITUTO DE PESQUISA ECONÔMICA APLICADA; FUNDAÇÃO JOÃO "
    "PINHEIRO. <b>O Índice de Desenvolvimento Humano Municipal Brasileiro</b>. Brasília: PNUD, Ipea, FJP, 2013. "
    "(Série Atlas do Desenvolvimento Humano no Brasil 2013).",
]:
    H.append(P(texto, "ref"))

H += [P("Reprodutibilidade", "h2")]
H += [P(
    "Todos os números, tabelas e gráficos deste relatório podem ser reproduzidos a partir do repositório do "
    "projeto: (1) <i>python codigos/01_preparacao_base.py</i> gera a base de análise; (2) o notebook "
    "<i>codigos/02_analise_estatistica.ipynb</i> executa as análises e grava os resultados e as figuras; "
    "(3) <i>python codigos/03_gerar_relatorio.py</i> monta este PDF. As instruções completas estão no README.md."
)]

# ----------------------------------------------------------------------------
# Geração do PDF
# ----------------------------------------------------------------------------
SAIDA.parent.mkdir(exist_ok=True)
doc = BaseDocTemplate(
    str(SAIDA), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=1.9 * cm,
    title="Relatório estatístico — Saneamento básico e mortalidade infantil nos municípios brasileiros",
    author="; ".join(nome for nome, _ in INTEGRANTES), subject="Global Solution CitizenTech — MLAM",
)
quadro = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="quadro",
               leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([
    PageTemplate(id="capa", frames=[quadro], onPage=capa, autoNextPageTemplate="conteudo"),
    PageTemplate(id="conteudo", frames=[quadro], onPage=cabecalho_rodape),
])
doc.build(H)
print(f"Relatório gerado: {SAIDA.relative_to(RAIZ)} ({doc.page} páginas)")
