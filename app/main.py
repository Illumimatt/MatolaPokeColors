"""Ponto de entrada do app.

Esse módulo só orquestra: carrega os dados iniciais e liga cada botão/input
da tela ao callback Python certo. Toda a lógica de verdade mora nos módulos
especializados (theme, pokemon_data, color_naming, ui, exportadores).
"""
import asyncio

from js import document, window
from pyodide.ffi import create_proxy

from app import color_naming
from app import pokemon_data
from app import theme
from app.exportadores import exportar_pantone_chart, exportar_paleta_imagem, exportar_paleta_stories
from app.ui import gerar_paleta, gerar_paleta_aleatoria

# Guarda referências vivas dos proxies criados aqui -- o Pyodide não pode
# coletar um create_proxy() enquanto o listener correspondente ainda
# existir no DOM.
_proxies = []


async def carregar_dados_iniciais():
    # Lê a paleta de cores do CSS antes de tudo, já que gerar_paleta() e as
    # funções de exportação dependem dela pra desenhar textos.
    theme.inicializar()

    if await pokemon_data.carregar_poke_data():
        # Dispara a geração automática direto, sem esperar o banco de nomes
        gerar_paleta(None)
        pokemon_data.preparar_busca_pokemon_js()

    if await pokemon_data.carregar_banco_cores():
        color_naming.preparar_banco_cores(pokemon_data.COLOR_DATA)

    gerar_paleta(None)


def _fechar_filtros_e_gerar(event=None):
    pokemon_data.invalidar_filtros()  # os checkboxes podem ter mudado
    gerar_paleta(event)


def _ligar_eventos():
    proxy_gerar_paleta = create_proxy(gerar_paleta)

    def atualizar_tela(event=None):
        # Pequeno delay (10ms) antes de regerar a paleta -- mesmo
        # comportamento do código original.
        window.setTimeout(proxy_gerar_paleta, 10)

    proxy_atualizar = create_proxy(atualizar_tela)
    proxy_fechar_filtros = create_proxy(_fechar_filtros_e_gerar)
    proxy_aleatorio = create_proxy(gerar_paleta_aleatoria)
    proxy_export_horizontal = create_proxy(exportar_paleta_imagem)
    proxy_export_stories = create_proxy(exportar_paleta_stories)
    proxy_export_moodboard = create_proxy(exportar_pantone_chart)

    document.getElementById("lista-cores").addEventListener("input", proxy_atualizar)
    document.getElementById("btn-add-cor").addEventListener("click", proxy_atualizar)
    document.getElementById("btn-fechar-filtros").addEventListener("click", proxy_fechar_filtros)
    document.querySelector("#btn-aleatorio").addEventListener("click", proxy_aleatorio)
    document.querySelector("#btn-exportar").addEventListener("click", proxy_export_horizontal)
    document.querySelector("#btn-stories").addEventListener("click", proxy_export_stories)
    document.querySelector("#btn-exportar_pantone_chart").addEventListener("click", proxy_export_moodboard)

    _proxies.extend([
        proxy_gerar_paleta, proxy_atualizar, proxy_fechar_filtros, proxy_aleatorio,
        proxy_export_horizontal, proxy_export_stories, proxy_export_moodboard,
    ])


_ligar_eventos()
asyncio.ensure_future(carregar_dados_iniciais())
