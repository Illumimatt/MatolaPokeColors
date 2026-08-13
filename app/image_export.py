"""Utilitários compartilhados pelas 3 imagens exportáveis (paleta horizontal,
stories vertical e moodboard Pantone).

No código original, cada uma das 3 funções de exportação duplicava: carregar
fontes, buscar/cachear sprite, desenhar texto quebrado em até 2 linhas, e o
fluxo inteiro de salvar/baixar (detecção de iOS, abrir aba nova vs. download
direto). Esse módulo existe pra que cada exportador (ver exportadores.py)
só precise descrever o SEU layout específico.
"""
import base64
from io import BytesIO

import requests
from PIL import Image, ImageFont
from js import window, document

from . import theme
from .config import CAMINHO_FONTE, TEXTO_LINK_SITE
from .i18n import t

# Cache de bytes de sprite já baixados (compartilhado pelas 3 exportações,
# já que é comum a mesma sessão exportar mais de um formato de imagem).
_SPRITE_CACHE = {}


def carregar_fontes(tamanhos):
    """tamanhos: dict tipo {"hex": 16, "pkmn": 16, "titulo": 30}.
    Retorna um dict com as mesmas chaves, apontando pro ImageFont carregado
    (ou pra fonte padrão do Pillow, se o .ttf não puder ser lido)."""
    try:
        return {chave: ImageFont.truetype(CAMINHO_FONTE, size=tamanho) for chave, tamanho in tamanhos.items()}
    except Exception as e:
        print(f"Erro ao carregar fonte do diretório, usando a padrão: {e}")
        return {chave: ImageFont.load_default() for chave in tamanhos}


def base_url_atual():
    """URL base do site (sem 'index.html' nem querystring/hash), usada pra
    montar o caminho absoluto dos sprites ao exportar a imagem."""
    href_atual = window.location.href.split("?")[0].split("#")[0]
    return href_atual.rsplit("/", 1)[0] if href_atual.endswith(".html") else href_atual.rstrip("/")


def buscar_sprite(id_pokemon, is_shiny, base_url, tamanho):
    """Baixa (ou reaproveita do cache) o sprite de um Pokémon já
    redimensionado pro tamanho pedido. Retorna None se não conseguir --
    quem chamou decide o que fazer nesse caso (pular, deixar espaço em
    branco etc)."""
    sufixo = "_shiny" if is_shiny else ""
    url = f"{base_url}/sprites/{id_pokemon}{sufixo}.png"

    if url not in _SPRITE_CACHE:
        try:
            resposta = requests.get(url, timeout=5)
            if resposta.status_code != 200:
                print(f"Sprite não encontrado: {url}")
                return None
            _SPRITE_CACHE[url] = resposta.content
        except Exception as e:
            print(f"Erro ao baixar sprite {url}: {e}")
            return None

    try:
        sprite = Image.open(BytesIO(_SPRITE_CACHE[url])).convert("RGBA")
        return sprite.resize((tamanho, tamanho), Image.NEAREST)
    except Exception as e:
        print(f"Erro ao processar sprite {url}: {e}")
        return None


def desenhar_texto_centralizado(draw, texto, x_centro, y, font, fill):
    """Desenha `texto` centralizado horizontalmente em torno de x_centro.
    Retorna a largura desenhada, caso o chamador precise dela."""
    bbox = draw.textbbox((0, 0), texto, font=font)
    largura = bbox[2] - bbox[0]
    draw.text((x_centro - largura // 2, y), texto, fill=fill, font=font)
    return largura


def desenhar_linhas_esquerda(draw, linhas, x, y, font, cores, espaco_entre_linhas):
    """Desenha várias linhas de texto alinhadas à esquerda, uma cor por
    linha (usado pro nome da cor, que pode vir em 1 ou 2 linhas com cores
    levemente diferentes por linha)."""
    for i, (linha, cor) in enumerate(zip(linhas, cores)):
        draw.text((x, y + i * espaco_entre_linhas), linha, fill=cor, font=font)


def desenhar_nome_pokemon_centralizado(draw, nome_completo, x_centro, y, font,
                                        cor_linha1, cor_linha2, espaco_entre_linhas):
    """Desenha o nome do Pokémon centralizado, quebrando em até 2 linhas no
    primeiro espaço (ex: 'Mega Charizard' -> 'Mega' / 'Charizard')."""
    if " " not in nome_completo:
        desenhar_texto_centralizado(draw, nome_completo, x_centro, y, font, cor_linha1)
        return
    linha1, linha2 = nome_completo.split(" ", 1)
    desenhar_texto_centralizado(draw, linha1, x_centro, y, font, cor_linha1)
    desenhar_texto_centralizado(draw, linha2, x_centro, y + espaco_entre_linhas, font, cor_linha2)


def desenhar_link_site(draw, largura_img, y, fonte, cor):
    """Desenha o link do site centralizado horizontalmente. Reaproveitado
    pelas 3 funções de exportação de imagem."""
    desenhar_texto_centralizado(draw, TEXTO_LINK_SITE, largura_img // 2, y, fonte, cor)


def exportar_imagem(img_final, nome_arquivo, chave_titulo_ios, chave_instrucao_ios):
    """Fluxo final compartilhado pelas 3 exportações: converte a imagem em
    PNG/base64 e decide entre baixar direto (desktop/Android) ou abrir numa
    aba nova com a instrução de 'segurar pra salvar' (iOS não permite
    download direto de imagens geradas em memória)."""
    try:
        buffered = BytesIO()
        img_final.save(buffered, format="PNG")
        data_url = f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"

        is_ios = "iPhone" in window.navigator.userAgent or "iPad" in window.navigator.userAgent
        if is_ios:
            _abrir_em_nova_aba_ios(data_url, t(chave_titulo_ios), t(chave_instrucao_ios))
        else:
            _baixar_diretamente(data_url, nome_arquivo)
    except Exception as e:
        print(f"Erro ao exportar imagem '{nome_arquivo}':", e)


def _baixar_diretamente(data_url, nome_arquivo):
    a = document.createElement("a")
    a.href = data_url
    a.download = nome_arquivo
    a.click()


def _abrir_em_nova_aba_ios(data_url, titulo, instrucao):
    nova_aba = window.open("", "_blank")
    if not nova_aba:
        # Bloqueador de pop-up do Safari impediu o window.open
        print("Por favor, permita pop-ups para visualizar e salvar sua imagem.")
        return
    nova_aba.document.write(f"""
        <html>
        <head>
            <title>{titulo}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ background: {theme.PALETA['fundo_imagem']}; color: {theme.PALETA['texto_secundario']}; margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: sans-serif; text-align: center; padding: 20px; box-sizing: border-box; }}
                img {{ max-width: 100%; max-height: 85vh; height: auto; border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.6); margin-bottom: 15px; }}
                p {{ font-size: 14px; letter-spacing: 0.05em; }}
            </style>
        </head>
        <body>
            <img src="{data_url}" alt="{titulo}">
            <p>{instrucao}</p>
        </body>
        </html>
    """)
    nova_aba.document.close()
