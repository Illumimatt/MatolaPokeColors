"""As 3 variações de imagem exportável: paleta horizontal, stories vertical
(9:16) e moodboard Pantone. Cada função só descreve o SEU layout -- toda a
lógica repetida (fontes, sprites, texto, salvar) mora em image_export.py.
"""
import math

from PIL import Image, ImageDraw
from js import document

from . import image_export as imgexp
from . import pokemon_data
from . import theme
from .color_math import hex_to_lab
from .color_naming import buscar_nome_cor, preparar_linhas_nome_cor
from .config import (
    QTD_POKEMON_PALETA_IMG,
    QTD_POKEMON_STORIES,
    TEXTO_CATEGORIA_PALETA,
    TEXTO_PANTONE_MATCH_PREFIXO,
    TEXTO_TITULO_PALETA,
    TEXTO_TITULO_PANTONE,
)


def _cores_hex_da_tela():
    return [el.value for el in document.querySelectorAll(".cor-input")]


def exportar_paleta_imagem(event=None):
    """Imagem horizontal: uma linha por cor, com o Pokémon mais próximo
    em cada uma das 7 posições ao lado."""
    if not pokemon_data.poke_data:
        return

    cores_hex = _cores_hex_da_tela()
    fontes = imgexp.carregar_fontes({"hex": 16, "pkmn": 16, "titulo": 30})

    largura_img = 1100
    espacamento_vertical = 140
    altura_titulo = 110
    altura_rodape = 50
    altura_img = altura_titulo + (len(cores_hex) * espacamento_vertical) + altura_rodape

    img_final = Image.new("RGB", (largura_img, altura_img), theme.PALETA["fundo_imagem"])
    draw = ImageDraw.Draw(img_final)

    imgexp.desenhar_texto_centralizado(
        draw, TEXTO_TITULO_PALETA, largura_img // 2, 30, fontes["titulo"], theme.PALETA["texto_secundario"]
    )

    dados_filtrados, permite_repetidos = pokemon_data.aplicar_filtros_avancados()
    base_url = imgexp.base_url_atual()
    ids_usados_global = set()
    largura_sprite = 96
    y_offset = altura_titulo

    for cor_hex in cores_hex:
        cor_lab = hex_to_lab(cor_hex)

        draw.rounded_rectangle([40, y_offset, 110, y_offset + 70], radius=8, fill=cor_hex)
        draw.text((42, y_offset + 80), cor_hex.upper(), fill=theme.PALETA["texto_secundario"], font=fontes["hex"])

        nome_cor = buscar_nome_cor(cor_hex, pokemon_data.COLOR_DATA)
        linhas_cor = preparar_linhas_nome_cor(nome_cor, largura_wrap=14)
        cores_linhas = [theme.PALETA["texto_terciario"], theme.PALETA["texto_quaternario"]]
        imgexp.desenhar_linhas_esquerda(draw, linhas_cor, 42, y_offset + 95, fontes["hex"], cores_linhas, 15)

        proximos = pokemon_data.selecionar_mais_proximos(
            cor_lab, dados_filtrados, permite_repetidos,
            ids_bloqueados=ids_usados_global, quantidade=QTD_POKEMON_PALETA_IMG,
        )
        if not permite_repetidos:
            ids_usados_global.update(p["id_base"] for p in proximos)

        x_offset = 160
        for pkmn in proximos:
            sprite = imgexp.buscar_sprite(pkmn["id_base"], "(Shiny)" in pkmn["name"], base_url, largura_sprite)
            if sprite is not None:
                img_final.paste(sprite, (x_offset, y_offset), sprite)
                imgexp.desenhar_nome_pokemon_centralizado(
                    draw, pkmn["name"], x_offset + largura_sprite // 2, y_offset + 95,
                    fontes["pkmn"], theme.PALETA["texto_primario"], theme.PALETA["texto_terciario"],
                    espaco_entre_linhas=15,
                )
            x_offset += 130

        y_offset += espacamento_vertical

    imgexp.desenhar_link_site(draw, largura_img, y_offset + 12, fontes["hex"], theme.PALETA["texto_terciario"])
    imgexp.exportar_imagem(img_final, "pokemon-palette.png", "ios_titulo_paleta", "ios_instrucao")


def exportar_paleta_stories(event=None):
    """Imagem vertical 9:16 pra Stories: uma coluna por cor, com os 5
    Pokémon mais próximos empilhados."""
    if not pokemon_data.poke_data:
        return

    cores_hex = _cores_hex_da_tela()
    fontes = imgexp.carregar_fontes({"hex": 24, "pkmn": 20, "titulo": 36})

    altura_img = 1920
    largura_coluna = 250
    padding_lateral = 50
    espacamento_entre = 30
    largura_sprite = 160
    largura_img = (padding_lateral * 2) + (len(cores_hex) * largura_coluna) + ((len(cores_hex) - 1) * espacamento_entre)

    img_final = Image.new("RGB", (largura_img, altura_img), theme.PALETA["fundo_imagem"])
    draw = ImageDraw.Draw(img_final)

    imgexp.desenhar_texto_centralizado(
        draw, TEXTO_TITULO_PALETA, largura_img // 2, 100, fontes["titulo"], theme.PALETA["texto_secundario"]
    )

    dados_filtrados, permite_repetidos = pokemon_data.aplicar_filtros_avancados()
    base_url = imgexp.base_url_atual()
    ids_usados_global = set()

    y_pokemon_start = 450
    espacamento_pkmn = 270

    for idx_coluna, cor_hex in enumerate(cores_hex):
        cor_lab = hex_to_lab(cor_hex)
        x_coluna = padding_lateral + (idx_coluna * (largura_coluna + espacamento_entre))
        x_centro_coluna = x_coluna + largura_coluna // 2

        x_rect_start = x_centro_coluna - 80
        draw.rounded_rectangle([x_rect_start, 220, x_rect_start + 160, 340], radius=14, fill=cor_hex)
        imgexp.desenhar_texto_centralizado(
            draw, cor_hex.upper(), x_centro_coluna, 355, fontes["hex"], theme.PALETA["texto_terciario"]
        )

        nome_cor = buscar_nome_cor(cor_hex, pokemon_data.COLOR_DATA)
        linhas_cor = preparar_linhas_nome_cor(nome_cor, largura_wrap=16)
        cores_linhas = [theme.PALETA["texto_terciario"], theme.PALETA["texto_quaternario"]]
        for i, (linha, cor) in enumerate(zip(linhas_cor, cores_linhas)):
            imgexp.desenhar_texto_centralizado(draw, linha, x_centro_coluna, 390 + i * 25, fontes["hex"], cor)

        proximos = pokemon_data.selecionar_mais_proximos(
            cor_lab, dados_filtrados, permite_repetidos,
            ids_bloqueados=ids_usados_global, quantidade=QTD_POKEMON_STORIES,
        )
        if not permite_repetidos:
            ids_usados_global.update(p["id_base"] for p in proximos)

        for idx_pkmn, pkmn in enumerate(proximos):
            sprite = imgexp.buscar_sprite(pkmn["id_base"], "(Shiny)" in pkmn["name"], base_url, largura_sprite)
            if sprite is None:
                continue
            y_sprite = y_pokemon_start + (idx_pkmn * espacamento_pkmn)
            img_final.paste(sprite, (x_centro_coluna - largura_sprite // 2, y_sprite), sprite)
            imgexp.desenhar_nome_pokemon_centralizado(
                draw, pkmn["name"], x_centro_coluna, y_sprite + 165,
                fontes["pkmn"], theme.PALETA["texto_primario"], theme.PALETA["texto_terciario"],
                espaco_entre_linhas=23,
            )

    imgexp.desenhar_link_site(draw, largura_img, altura_img - 60, fontes["hex"], theme.PALETA["texto_terciario"])
    imgexp.exportar_imagem(img_final, "pokemon-palette-stories.png", "ios_titulo_stories", "ios_instrucao_stories")


def exportar_pantone_chart(event=None):
    """Moodboard em grade 2 colunas, estilo cartela Pantone: um card por
    cor, com o nome oficial Pantone quando existe, ou o nome aproximado
    (banco de 32 mil cores) caso contrário."""
    if not pokemon_data.poke_data:
        return

    cores_hex = _cores_hex_da_tela()
    fontes = imgexp.carregar_fontes({"hex": 24, "pkmn": 20, "titulo": 36})
    branco = theme.PALETA["branco"]

    largura_card, altura_card, padding, colunas, altura_rodape = 500, 420, 40, 2, 50
    num_linhas = math.ceil(len(cores_hex) / colunas)
    largura_img = (colunas * largura_card) + ((colunas + 1) * padding)
    altura_img = (num_linhas * altura_card) + ((num_linhas + 1) * padding) + 100 + altura_rodape

    img_final = Image.new("RGB", (largura_img, altura_img), theme.PALETA["fundo_imagem"])
    draw = ImageDraw.Draw(img_final)
    draw.text((padding, 20), TEXTO_TITULO_PANTONE, fill=branco, font=fontes["titulo"])

    dados_filtrados, _ = pokemon_data.aplicar_filtros_avancados()
    base_url = imgexp.base_url_atual()

    for i, cor_hex in enumerate(cores_hex):
        coluna, linha = i % colunas, i // colunas
        x_bloco = padding + (coluna * (largura_card + padding))
        y_bloco = 120 + (linha * (altura_card + padding))

        draw.rectangle([x_bloco, y_bloco, x_bloco + largura_card, y_bloco + altura_card], fill=cor_hex)
        hex_chave = cor_hex.upper()
        info = pokemon_data.COLOR_DATA.get(hex_chave)

        if info and "code" in info and "cat" in info:
            # Cor bate exatamente com uma entrada Pantone conhecida
            draw.text((x_bloco + 20, y_bloco + 20), info["cat"].upper(), fill=branco, font=fontes["pkmn"])
            draw.text((x_bloco + 20, y_bloco + 50), info["name"], fill=branco, font=fontes["titulo"])
            draw.text((x_bloco + 20, y_bloco + 320), hex_chave, fill=branco, font=fontes["hex"])
            draw.text(
                (x_bloco + 20, y_bloco + 350), f"{TEXTO_PANTONE_MATCH_PREFIXO}{info['code']}",
                fill=branco, font=fontes["pkmn"],
            )
        else:
            # Cor customizada: usa o nome aproximado do banco de 32 mil cores
            nome_aproximado = buscar_nome_cor(cor_hex, pokemon_data.COLOR_DATA)
            linhas_cor = preparar_linhas_nome_cor(nome_aproximado, largura_wrap=15)
            cores_linhas = [branco, theme.PALETA["texto_destaque"]]

            draw.text((x_bloco + 20, y_bloco + 20), TEXTO_CATEGORIA_PALETA, fill=branco, font=fontes["pkmn"])
            imgexp.desenhar_linhas_esquerda(draw, linhas_cor, x_bloco + 20, y_bloco + 50, fontes["titulo"], cores_linhas, 45)
            draw.text((x_bloco + 20, y_bloco + 320), hex_chave, fill=branco, font=fontes["hex"])

        # Sprite do Pokémon mais próximo (aqui não há preocupação com
        # repetição entre cards -- cada cor busca seu vizinho mais próximo
        # de forma independente, por isso permite_repetidos=True)
        cor_lab = hex_to_lab(cor_hex)
        candidato = pokemon_data.selecionar_mais_proximos(cor_lab, dados_filtrados, permite_repetidos=True, quantidade=1)[0]
        sprite = imgexp.buscar_sprite(candidato["id_base"], "(Shiny)" in candidato["name"], base_url, 160)
        if sprite is not None:
            img_final.paste(sprite, (x_bloco + 300, y_bloco + 180), sprite)

    imgexp.desenhar_link_site(draw, largura_img, altura_img - 40, fontes["hex"], theme.PALETA["texto_terciario"])
    imgexp.exportar_imagem(img_final, "pokemon-pantone-birth-chart-palette.png", "ios_titulo_moodboard", "ios_instrucao")
