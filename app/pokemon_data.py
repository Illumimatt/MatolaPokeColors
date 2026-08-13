"""Dataset de Pokémon: carregamento, filtros avançados e seleção dos mais
próximos de uma cor.

`poke_data` e `COLOR_DATA` nunca são reatribuídos (sempre .clear()+.update()
ou .clear()+.extend()) pelo mesmo motivo explicado em theme.py: preserva a
identidade do objeto, então "from app.pokemon_data import poke_data" em
outro módulo continua válido depois que os dados terminam de carregar.
"""
import heapq

from js import document
from pyodide.http import pyfetch

from .color_math import color_distance

# Lista de todos os Pokémon (normal + shiny) com cor, tipo, geração etc.
# Ver pokemon_colors_simple.json para o formato de cada item.
poke_data = []

# Banco de ~32 mil nomes de cor (hex -> {"name": ..., opcionalmente "code"/"cat"
# pra cores que batem com o Pantone Birth Chart). Ver cores_finais.json.
COLOR_DATA = {}

# Cache dos filtros avançados: só reprocessa quando algo realmente mudou
# (dirty flag clássico -- os checkboxes do modal são lidos do DOM, o que não
# é gratuito, então evitamos reler/refiltrar a cada cor gerada).
_filtros_cache = None
_filtros_sujos = True


async def carregar_poke_data():
    """Busca pokemon_colors_simple.json. Retorna True se deu certo."""
    try:
        response = await pyfetch("pokemon_colors_simple.json")
        if response.status != 200:
            return False
        dados = await response.json()
        poke_data.clear()
        poke_data.extend(dados)
        print("Dados dos Pokémon carregados com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao carregar dados dos Pokémon: {e}")
        return False


async def carregar_banco_cores():
    """Busca cores_finais.json. Retorna True se deu certo."""
    try:
        resp = await pyfetch("./cores_finais.json")
        dados = await resp.json()
        COLOR_DATA.clear()
        COLOR_DATA.update(dados)
        return True
    except Exception as e:
        print(f"Erro ao carregar cores_finais.json: {e}")
        return False


def invalidar_filtros():
    """Força aplicar_filtros_avancados() a reler os checkboxes na próxima
    chamada. Chamado depois que o modal de filtros é fechado, já que os
    checkboxes podem ter mudado."""
    global _filtros_sujos
    _filtros_sujos = True


def aplicar_filtros_avancados():
    """Lê os checkboxes do modal de filtros e devolve (pokemons_filtrados,
    permite_repetidos). Resultado é cacheado até o próximo invalidar_filtros()."""
    global _filtros_cache, _filtros_sujos

    if not _filtros_sujos and _filtros_cache is not None:
        return _filtros_cache

    # 1. Regras únicas
    chk_repetidos = document.getElementById("chk-repetidos").checked
    chk_shiny_only = document.getElementById("chk-apenas-shiny").checked
    chk_no_shiny = document.getElementById("chk-sem-shiny").checked

    chk_estagio_1 = document.getElementById("chk-estagio-1").checked
    chk_estagio_2 = document.getElementById("chk-estagio-2").checked
    chk_estagio_final = document.getElementById("chk-estagio-final").checked
    chk_megas = document.getElementById("chk-megas").checked
    chk_lendarios_miticos = document.getElementById("chk-lendarios-miticos").checked

    # 2. Listas de checkboxes (Gerações, Tipos, Habitats)
    gens_selecionadas = [el.value for el in document.querySelectorAll(".chk-gen") if el.checked]
    tipos_selecionados = [el.value for el in document.querySelectorAll(".chk-type") if el.checked]
    habitats_selecionados = [el.value for el in document.querySelectorAll(".chk-habitat") if el.checked]

    dados_filtrados = []
    for p in poke_data:
        is_shiny = "(Shiny)" in p["name"]
        if chk_shiny_only and not is_shiny:
            continue
        if chk_no_shiny and is_shiny:
            continue

        if chk_estagio_1 and p.get("evolution_stage") != 1:
            continue
        if chk_estagio_2 and not (p.get("evolution_stage") == 2 and not p.get("is_fully_evolved", False)):
            continue
        if chk_estagio_final and not p.get("is_fully_evolved", False):
            continue
        if chk_megas and not p.get("is_mega", False):
            continue
        if chk_lendarios_miticos and not (p.get("is_legendary", False) or p.get("is_mythical", False)):
            continue

        if gens_selecionadas and p.get("generation") not in gens_selecionadas:
            continue
        if habitats_selecionados and p.get("habitat") not in habitats_selecionados:
            continue

        if tipos_selecionados:
            tipos_do_pokemon = p.get("types", [])
            if not any(tp in tipos_selecionados for tp in tipos_do_pokemon):
                continue

        dados_filtrados.append(p)

    _filtros_cache = (dados_filtrados, chk_repetidos)
    _filtros_sujos = False
    return _filtros_cache


def _sem_ids_repetidos(candidatos_ordenados, quantidade):
    resultado = []
    ids_vistos = set()
    for p in candidatos_ordenados:
        if p["id_base"] in ids_vistos:
            continue
        ids_vistos.add(p["id_base"])
        resultado.append(p)
        if len(resultado) == quantidade:
            break
    return resultado


def selecionar_mais_proximos(cor_lab, candidatos, permite_repetidos, ids_bloqueados=None,
                              quantidade=7, buffer_candidatos=40):
    """Pega os `quantidade` Pokémon mais próximos de uma cor.

    - `ids_bloqueados`: ids já usados por OUTRAS cores da paleta (colunas
      anteriores), pra não repetir o mesmo Pokémon entre colunas diferentes
      quando `permite_repetidos` é False. Passe None (ou omita) se isso não
      importa no seu contexto -- ex: o moodboard Pantone escolhe 1 Pokémon
      por cor independentemente, então cada card pode chamar com
      `permite_repetidos=True, quantidade=1` pra pegar só o vizinho mais
      próximo, sem se importar com repetição.
    - Quando `permite_repetidos` é False, cada `id_base` aparece no máximo
      uma vez no resultado, mesmo que o Pokémon tenha 2 entradas na base
      (normal + shiny, com cores diferentes).

    Essa função substitui DUAS implementações que existiam no código
    original: uma (mais rápida, com buffer) usada só na tela, e outra (mais
    simples, ordenando tudo) usada nas 3 imagens exportadas -- e que, por
    não rastrear `ids_bloqueados` entre colunas, deixava a mesma cor repetir
    Pokémon na imagem final mesmo com "Permitir Repetidos" desmarcado.
    Unificar aqui corrige essa inconsistência: tela e imagem exportada agora
    sempre mostram exatamente o mesmo resultado.
    """
    ids_bloqueados = ids_bloqueados or set()
    disponiveis = candidatos if permite_repetidos else [
        p for p in candidatos if p["id_base"] not in ids_bloqueados
    ]

    if permite_repetidos:
        return heapq.nsmallest(quantidade, disponiveis, key=lambda p: color_distance(cor_lab, p["color"]))

    # Pega uma "sobra" de candidatos (não só `quantidade`) porque cada
    # Pokémon pode aparecer 2x na base (normal + shiny) com cores
    # diferentes -- sem esse buffer, as duas versões do mesmo Pokémon
    # poderiam cair entre os mais próximos DESTA MESMA coluna.
    candidatos_proximos = heapq.nsmallest(
        buffer_candidatos, disponiveis, key=lambda p: color_distance(cor_lab, p["color"])
    )
    resultado = _sem_ids_repetidos(candidatos_proximos, quantidade)

    # Caso raríssimo: o buffer não tinha IDs únicos suficientes (filtros
    # muito restritos). Refaz varrendo tudo, sem limite de buffer.
    if len(resultado) < quantidade and len(disponiveis) > buffer_candidatos:
        candidatos_completos = sorted(disponiveis, key=lambda p: color_distance(cor_lab, p["color"]))
        resultado = _sem_ids_repetidos(candidatos_completos, quantidade)

    return resultado
