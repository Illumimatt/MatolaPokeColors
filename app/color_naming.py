"""Nomeação de cores: dado um hex, acha o nome mais parecido num banco de
~32 mil cores (estilo cartela de tintas/Pantone).

Esse "banco de cores" e a flag de "tá pronto?" moram só aqui dentro -- outros
módulos nunca leem/escrevem essas variáveis diretamente, só chamam as duas
funções públicas (buscar_nome_cor e preparar_banco_cores). Isso evita a
armadilha de import de estado mutável entre módulos (ver comentário em
theme.py) e deixa claro quem é dono desse estado.
"""
import textwrap
import unicodedata

from js import window

from .color_math import hex_to_lab

# Cache de nomes de cor já resolvidos (hex -> nome), evita rebuscar a mesma
# cor repetidamente.
_NOME_COR_CACHE = {}

# Só fica True depois que o banco de ~32 mil cores foi enviado pro JS. Evita
# que a 1ª renderização (que roda antes desse banco carregar) grave
# "Custom Color" no cache pra sempre.
_banco_pronto = False


def preparar_banco_cores(color_data):
    """Pré-calcula o Lab de cada cor do banco (uma única vez) e manda pro
    JS, que faz a busca de cor mais próxima nativamente (loop em V8 é bem
    mais rápido que o mesmo loop rodando em Python/Pyodide).

    Chamado uma vez, depois que cores_finais.json termina de carregar.
    """
    global _banco_pronto

    lista_para_js = []
    for hex_key, dados in color_data.items():
        if not hex_key.startswith("#"):
            continue
        L, a, b = hex_to_lab(hex_key)
        lista_para_js.append({"name": dados.get("name", "Custom Color"), "l": L, "a": a, "b": b})

    window.prepararBancoCoresJS(lista_para_js)
    _banco_pronto = True
    print(f"Banco de {len(lista_para_js)} cores preparado no JS.")


def buscar_nome_cor(cor_hex, banco_cores):
    """Acha o nome de uma cor: match exato no banco, cache, ou busca
    aproximada (delegada pro JS, ver preparar_banco_cores)."""
    cor_hex_upper = cor_hex.upper()

    # 1. Cache: se já buscamos essa cor exata antes, retorna na hora
    if cor_hex_upper in _NOME_COR_CACHE:
        return _NOME_COR_CACHE[cor_hex_upper]

    # 2. Match exato no banco de cores (sempre confiável, pode cachear)
    if cor_hex_upper in banco_cores:
        nome_exibido = banco_cores[cor_hex_upper].get("name", "Custom Color")
        _NOME_COR_CACHE[cor_hex_upper] = nome_exibido
        return nome_exibido

    # 3. Busca aproximada: delegada pro JS
    lab_alvo = hex_to_lab(cor_hex)
    try:
        nome_exibido = window.buscarNomeCorJS(lab_alvo)
    except Exception as e:
        print(f"Erro ao buscar nome de cor via JS: {e}")
        nome_exibido = "Custom Color"

    # Só grava no cache se o banco já estiver carregado de verdade. Caso
    # contrário, essa resposta é só um "Custom Color" provisório (banco
    # ainda vazio) e não pode virar cache permanente.
    if _banco_pronto:
        _NOME_COR_CACHE[cor_hex_upper] = nome_exibido

    return nome_exibido


def remover_acentos_para_imagem(texto):
    """Transforma 'ā' em 'a', 'é' em 'e' etc -- a fonte pixel usada nas
    imagens exportadas não tem os glifos acentuados."""
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def preparar_linhas_nome_cor(nome_cor, largura_wrap):
    """Limpa acentos e quebra o nome da cor em linhas de até `largura_wrap`
    caracteres -- usado pelas 3 imagens exportadas, que só diferem na
    largura de quebra."""
    nome_limpo = remover_acentos_para_imagem(nome_cor)
    return textwrap.wrap(nome_limpo, width=largura_wrap)
