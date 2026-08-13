"""Renderização dos resultados na tela: para cada cor escolhida, monta uma
linha com o seletor de cor + os N Pokémon mais próximos.

Toda a aparência (tamanhos, cores, hover) fica em style.css -- aqui só
criamos os elementos e plugamos as classes certas. No código original, cada
elemento tinha ~8 linhas de ".style.propriedade = valor" atribuídas na mão
em Python; isso duplicava o que já dava pra descrever em CSS (inclusive o
efeito de "aumentar o sprite ao passar o mouse", que era feito com
onmouseover/onmouseout em Python e agora é só um :hover no CSS).
"""
import random

from js import document
from pyodide.ffi import create_proxy

from . import pokemon_data
from .color_math import hex_to_lab
from .color_naming import buscar_nome_cor
from .config import QTD_POKEMON_TELA
from .i18n import t


def gerar_paleta(event=None):
    if not pokemon_data.poke_data:
        print("Os dados dos Pokémon ainda estão sendo carregados. Aguarde um instante...")
        return

    elementos_cor = document.querySelectorAll(".cor-input")
    elementos_texto = document.querySelectorAll(".hex-input")
    container = document.querySelector("#output-container")
    container.innerHTML = ""

    dados_filtrados, permite_repetidos = pokemon_data.aplicar_filtros_avancados()
    ids_usados_global = set()

    for i in range(len(elementos_cor)):
        cor_hex = elementos_cor[i].value
        cor_lab = hex_to_lab(cor_hex)

        row = _criar_linha_resultado(cor_hex, i, elementos_cor, elementos_texto)

        proximos = pokemon_data.selecionar_mais_proximos(
            cor_lab, dados_filtrados, permite_repetidos,
            ids_bloqueados=ids_usados_global, quantidade=QTD_POKEMON_TELA,
        )
        if not permite_repetidos:
            ids_usados_global.update(p["id_base"] for p in proximos)

        for pkmn in proximos:
            row.appendChild(_criar_cartao_pokemon(pkmn))

        container.appendChild(row)


def _criar_linha_resultado(cor_hex, indice, elementos_cor, elementos_texto):
    row = document.createElement("div")
    row.className = "color-row"

    color_container = document.createElement("div")
    color_container.className = "grupo-cor-editavel"

    color_box = document.createElement("input")
    color_box.type = "color"
    color_box.value = cor_hex
    color_box.className = "cor-editavel-bot"

    color_text = document.createElement("input")
    color_text.type = "text"
    color_text.value = cor_hex.upper()
    color_text.maxLength = 7
    color_text.className = "hex-input-editavel"

    nome_cor = buscar_nome_cor(cor_hex, pokemon_data.COLOR_DATA)
    name_display = document.createElement("div")
    name_display.innerText = nome_cor
    name_display.className = "nome-cor-detectado"

    proxy_sync = _criar_sincronizador(indice, elementos_cor, elementos_texto)
    color_box.addEventListener("change", proxy_sync)
    color_text.addEventListener("change", proxy_sync)
    # Guarda a referência do proxy no próprio elemento pra não ser coletada
    # pelo Pyodide enquanto o elemento ainda existir no DOM.
    color_box._proxy_sync = proxy_sync

    color_container.appendChild(color_box)
    color_container.appendChild(color_text)
    color_container.appendChild(name_display)
    row.appendChild(color_container)
    return row


def _criar_sincronizador(index, elementos_cor, elementos_texto):
    """Mantém o color picker (input type=color) e o campo de texto hex
    sincronizados quando editados diretamente num card já gerado."""
    def sincronizar(e):
        novo_valor = e.target.value.strip()
        if len(novo_valor) == 7 and novo_valor.startswith("#"):
            elementos_cor[index].value = novo_valor
            elementos_texto[index].value = novo_valor.upper()
            gerar_paleta(None)
        else:
            e.target.value = elementos_texto[index].value.upper()
    return create_proxy(sincronizar)


def _criar_cartao_pokemon(pkmn):
    pkmn_box = document.createElement("div")
    pkmn_box.className = "cartao-pokemon"

    id_pokemon = pkmn["id_base"]
    sufixo = "_shiny" if "(Shiny)" in pkmn["name"] else ""

    img = document.createElement("img")
    img.src = f"./sprites/{id_pokemon}{sufixo}.png"
    img.className = "sprite-pokemon"
    img.title = f"{pkmn['name']} {t('tooltip_clique_salvar')}"

    name_tag = document.createElement("span")
    name_tag.innerText = pkmn["name"]
    name_tag.className = "nome-pokemon-card"

    pkmn_box.appendChild(img)
    pkmn_box.appendChild(name_tag)
    return pkmn_box


def gerar_paleta_aleatoria(event=None):
    elementos_cor = document.querySelectorAll(".cor-input")
    elementos_texto = document.querySelectorAll(".hex-input")

    for i in range(len(elementos_cor)):
        hex_aleatorio = "#{:06X}".format(random.randint(0, 0xFFFFFF))
        elementos_cor[i].value = hex_aleatorio
        elementos_texto[i].value = hex_aleatorio

    gerar_paleta(None)
