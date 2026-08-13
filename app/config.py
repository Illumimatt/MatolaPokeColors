"""Constantes compartilhadas por todo o app.

Centralizar aqui evita "números mágicos" espalhados pelos módulos de
exportação e facilita ajustar coisas como quantidade de Pokémon exibidos
sem precisar caçar o valor em 3 lugares diferentes.
"""

CAMINHO_FONTE = "fonts/VCR_OSD_MONO_1.001.ttf"

# --- TEXTOS FIXOS DAS IMAGENS EXPORTADAS (sempre em inglês) ---
# Mesmo raciocínio do --export-bg no CSS: a imagem baixada/compartilhada
# deve ficar igual pra todo mundo, independente do idioma da interface de
# quem a gerou -- e nomes de arquivo/texto em inglês funcionam melhor
# universalmente (hashtags, buscas etc). NÃO usam t()/TRADUCOES de propósito.
TEXTO_TITULO_PALETA = "MY POKÉMON PALETTE"
TEXTO_TITULO_PANTONE = "MY POKÉMON PANTONE BIRTH CHART PALETTE"
TEXTO_CATEGORIA_PALETA = "PALETTE"
TEXTO_PANTONE_MATCH_PREFIXO = "Pantone match: "
TEXTO_LINK_SITE = "illumimatt.github.io/MatolaPokeColors/"

# NOTA: os textos dos pop-ups do iOS (título da aba, instrução de "segure
# pra salvar") NÃO ficam fixos -- são a tela que a PESSOA vê enquanto salva,
# não pixels da imagem em si, então usam t() e seguem o idioma do site
# (ver app/i18n.py e as chamadas em app/exportadores.py).

# Quantos Pokémon mostrar por cor, em cada contexto onde isso é usado
QTD_POKEMON_TELA = 7
QTD_POKEMON_PALETA_IMG = 7
QTD_POKEMON_STORIES = 5
