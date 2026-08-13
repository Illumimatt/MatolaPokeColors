"""Paleta de cores usada pelo Python (imagens PNG exportadas + pop-up do iOS).

Fonte única de verdade: as cores moram no :root do style.css. Aqui a gente
só LÊ os valores (via getComputedStyle) e guarda em cache -- mudar uma cor
no CSS reflete automaticamente na interface E nas imagens exportadas, sem
precisar tocar em nada aqui.

IMPORTANTE (armadilha comum ao dividir um script em módulos): PALETA nunca
é reatribuído com "PALETA = {...}" -- isso criaria um dict novo e qualquer
outro módulo que já tivesse feito "from app.theme import PALETA" continuaria
enxergando o dict antigo (vazio). Em vez disso, sempre fazemos
PALETA.clear() + PALETA.update(...), mutando o MESMO objeto, para que
qualquer import feito em outro módulo continue válido depois que os dados
carregarem.
"""
from js import window, document

_CSS_VARS_CACHE = {}

# Populado de verdade por inicializar(), chamado uma vez quando o DOM já
# está garantidamente pronto pra leitura via getComputedStyle.
PALETA = {}


def _cor_css(nome_var, fallback):
    """Lê uma CSS custom property (ex: '--export-bg') do :root.
    Resultado é cacheado, já que essas cores não mudam em runtime."""
    if nome_var in _CSS_VARS_CACHE:
        return _CSS_VARS_CACHE[nome_var]
    try:
        valor = window.getComputedStyle(document.documentElement).getPropertyValue(nome_var).strip()
        resultado = valor if valor else fallback
    except Exception as e:
        print(f"Erro ao ler CSS var {nome_var}, usando fallback: {e}")
        resultado = fallback
    _CSS_VARS_CACHE[nome_var] = resultado
    return resultado


def inicializar():
    """Popula PALETA a partir das CSS vars. Chamado uma vez no início do app.

    Os valores de fallback são os hex que já estavam hardcoded no código
    antes dessa mudança -- garantem que nada quebra mesmo se o CSS falhar
    ao carregar por algum motivo.

    As chaves "texto_*" e "fundo_imagem" leem as CSS vars --export-*, que
    são FIXAS (não mudam entre modo claro/escuro) -- usadas só nas imagens
    PNG exportadas e no popup de salvar do iOS, pra manter a estética da
    imagem consistente pra quem recebe. Já "ui_secundario" lê
    --muted-foreground, que SE ADAPTA ao tema do dispositivo -- é pra texto
    que aparece direto na tela (DOM), não em imagem.
    """
    novos_valores = {
        "fundo_imagem":      _cor_css("--export-bg", "#1b1b1b"),
        "texto_primario":    _cor_css("--export-text-primary", "#FFFFF0"),
        "texto_secundario":  _cor_css("--export-text-secondary", "#cbd5e1"),
        "texto_terciario":   _cor_css("--export-text-tertiary", "#94a3b8"),
        "texto_quaternario": _cor_css("--export-text-quaternary", "#64748b"),
        "texto_destaque":    _cor_css("--export-text-highlight", "#e2e8f0"),
        "ui_secundario":     _cor_css("--muted-foreground", "#98a6b3"),
        "branco":            "white",
    }
    PALETA.clear()
    PALETA.update(novos_valores)
    return PALETA
