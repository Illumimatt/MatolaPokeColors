from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from js import window, document
import base64, math, random, asyncio, requests, unicodedata, textwrap, heapq
from pyodide.http import pyfetch
from pyodide.ffi import create_proxy

# --- INTERNACIONALIZAÇÃO (i18n) ---
# Fonte única de verdade: TRADUCOES em script.js. O Python só consulta,
# não duplica o dicionário — assim um texto novo em script.js já fica
# disponível aqui de graça, sem precisar traduzir em dois lugares.
def t(chave):
    """Traduz uma chave usando o idioma ativo (detectado em script.js)."""
    try:
        return window.t(chave)
    except Exception as e:
        print(f"Erro ao traduzir chave '{chave}': {e}")
        return chave

# --- PALETA DE CORES CENTRALIZADA ---
# Fonte única de verdade: as cores moram no :root do style.css.
# Aqui a gente só LÊ os valores (via getComputedStyle) e guarda em cache —
# mudar uma cor no CSS reflete automaticamente na interface E nas imagens
# PNG exportadas, sem precisar tocar em nada aqui.
_CSS_VARS_CACHE = {}

def cor_css(nome_var, fallback):
    """Lê uma CSS custom property (ex: '--text-primary-img') do :root.
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

def carregar_paleta():
    """Popula a PALETA a partir das CSS vars. Chamado uma vez no início.
    Os valores de fallback são os hex que já estavam hardcoded no código
    antes dessa mudança — garantem que nada quebra mesmo se o CSS falhar
    ao carregar por algum motivo.

    IMPORTANTE: as chaves "texto_*" e "fundo_imagem" leem as CSS vars
    --export-*, que são FIXAS (não mudam entre modo claro/escuro) — são
    usadas só nas imagens PNG exportadas e no popup de salvar do iOS, pra
    manter a estética da imagem consistente pra quem recebe.
    Já "ui_secundario" lê --muted-foreground, que SE ADAPTA ao tema do
    dispositivo — é pra texto que aparece direto na tela (DOM), não em
    imagem."""
    return {
        "fundo_imagem":      cor_css("--export-bg", "#1b1b1b"),
        "texto_primario":    cor_css("--export-text-primary", "#FFFFF0"),
        "texto_secundario":  cor_css("--export-text-secondary", "#cbd5e1"),
        "texto_terciario":   cor_css("--export-text-tertiary", "#94a3b8"),
        "texto_quaternario": cor_css("--export-text-quaternary", "#64748b"),
        "texto_destaque":    cor_css("--export-text-highlight", "#e2e8f0"),
        "ui_secundario":     cor_css("--muted-foreground", "#98a6b3"),
        "branco":            "white",
    }

# Preenchida de verdade na primeira chamada de carregar_dados_iniciais(),
# quando o DOM já está garantidamente pronto pra leitura via getComputedStyle.
PALETA = {}

# --- VARIÁVEL GLOBAL PARA GUARDAR OS DADOS ---
SPRITE_CACHE = {}
COLOR_DATA = {}
poke_data = []

# Cache de nomes de cor já resolvidos (hex -> nome), evita rebuscar a mesma cor
NOME_COR_CACHE = {}

# Só fica True depois que o banco de ~32 mil cores foi enviado pro JS.
# Evita que a 1ª renderização (que roda antes desse banco carregar) grave
# "Custom Color" no cache pra sempre.
BANCO_CORES_PRONTO = False

# Cache dos filtros avançados: só reprocessa quando algo realmente mudou
FILTROS_CACHE = None
FILTROS_SUJOS = True

def rgb_to_lab(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    def gamma(c):
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92

    r = gamma(r)
    g = gamma(g)
    b = gamma(b)

    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) * 100
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) * 100
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) * 100

    x /= 95.047
    y /= 100.000
    z /= 108.883

    def f(t):
        if t > 0.008856:
            return t ** (1 / 3)
        return 7.787 * t + 16 / 116

    fx = f(x)
    fy = f(y)
    fz = f(z)

    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return [L, a, b]

def parse_input_color(hex_color):
    hex_color = hex_color.strip().replace("#", "")
    return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]

def color_distance(lab1, lab2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))

def buscar_nome_cor(cor_hex, banco_cores):
    cor_hex_upper = cor_hex.upper()

    # 1. Cache: se já buscamos essa cor exata antes, retorna na hora
    if cor_hex_upper in NOME_COR_CACHE:
        return NOME_COR_CACHE[cor_hex_upper]

    # 2. Match exato no banco de cores (sempre confiável, pode cachear)
    if cor_hex_upper in banco_cores:
        nome_exibido = banco_cores[cor_hex_upper].get("name", "Custom Color")
        NOME_COR_CACHE[cor_hex_upper] = nome_exibido
        return nome_exibido

    # 3. Busca aproximada: delegada pro JS
    lab_alvo = rgb_to_lab(*parse_input_color(cor_hex))
    try:
        nome_exibido = window.buscarNomeCorJS(lab_alvo)
    except Exception as e:
        print(f"Erro ao buscar nome de cor via JS: {e}")
        nome_exibido = "Custom Color"

    # Só grava no cache se o banco já estiver carregado de verdade.
    # Caso contrário, essa resposta é só um "Custom Color" provisório
    # (banco ainda vazio) e não pode virar cache permanente.
    if BANCO_CORES_PRONTO:
        NOME_COR_CACHE[cor_hex_upper] = nome_exibido

    return nome_exibido
    
def remover_acentos_para_imagem(texto):
    # Transforma "ā" em "a", "é" em "e", etc.
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def aplicar_filtros_avancados():
    global FILTROS_CACHE, FILTROS_SUJOS

    # Se nada mudou desde a última vez, devolve o resultado já calculado
    if not FILTROS_SUJOS and FILTROS_CACHE is not None:
        return FILTROS_CACHE

    # 1. Lê os checkboxes de regras únicas
    chk_repetidos = document.getElementById("chk-repetidos").checked
    chk_shiny_only = document.getElementById("chk-apenas-shiny").checked
    chk_no_shiny = document.getElementById("chk-sem-shiny").checked
    
    chk_estagio_1 = document.getElementById("chk-estagio-1").checked
    chk_estagio_2 = document.getElementById("chk-estagio-2").checked
    chk_estagio_final = document.getElementById("chk-estagio-final").checked
    chk_megas = document.getElementById("chk-megas").checked
    chk_lendarios_miticos = document.getElementById("chk-lendarios-miticos").checked

    # 2. Lê as listas de checkboxes (Gerações, Tipos, Habitats)
    gens_selecionadas = [el.value for el in document.querySelectorAll(".chk-gen") if el.checked]
    tipos_selecionados = [el.value for el in document.querySelectorAll(".chk-type") if el.checked]
    habitats_selecionados = [el.value for el in document.querySelectorAll(".chk-habitat") if el.checked]

    dados_filtrados = []
    
    for p in poke_data:
        # Filtros de Shiny
        is_shiny = "(Shiny)" in p["name"]
        if chk_shiny_only and not is_shiny: continue
        if chk_no_shiny and is_shiny: continue
        
        # Filtros de Biologia
        if chk_estagio_1 and p.get("evolution_stage") != 1: continue
        if chk_estagio_2 and not (p.get("evolution_stage") == 2 and not p.get("is_fully_evolved", False)): continue
        if chk_estagio_final and not p.get("is_fully_evolved", False): continue
        if chk_megas and not p.get("is_mega", False): continue
        if chk_lendarios_miticos and not (p.get("is_legendary", False) or p.get("is_mythical", False)): continue
        
        # Filtros de Listas (Se o usuário marcou alguma coisa, tem que bater)
        if gens_selecionadas and p.get("generation") not in gens_selecionadas: continue
        if habitats_selecionados and p.get("habitat") not in habitats_selecionados: continue
        
        # Filtro de Tipo (Checa se ALGUM dos tipos do Pokémon bate com os marcados)
        if tipos_selecionados:
            tipos_do_pokemon = p.get("types", [])
            if not any(t in tipos_selecionados for t in tipos_do_pokemon):
                continue
        
        # Se passou por todas as barreiras, está aprovado!
        dados_filtrados.append(p)

    FILTROS_CACHE = (dados_filtrados, chk_repetidos)
    FILTROS_SUJOS = False
    return FILTROS_CACHE

# --- FUNÇÃO PRINCIPAL DE GERAR PALETA ---
def gerar_paleta(event=None):
    global poke_data
    if not poke_data:
        print("Os dados dos Pokémon ainda estão sendo carregados. Aguarde um instante...")
        return

    elementos_cor = document.querySelectorAll(".cor-input")
    elementos_texto = document.querySelectorAll(".hex-input")
    container = document.querySelector("#output-container")
    container.innerHTML = ""
    dados_filtrados, permite_repetidos = aplicar_filtros_avancados()
    ids_usados_global = set()

    # Loop de Cores
    for i in range(len(elementos_cor)):
        cor_hex = elementos_cor[i].value
        cor_lab = rgb_to_lab(*parse_input_color(cor_hex))
        
        # Criação da linha da cor (mantém sua estrutura visual limpa via classes do CSS)
        row = document.createElement("div")
        row.className = "color-row"
        row.style.display = "flex"
        row.style.alignItems = "center"
        row.style.marginBottom = "5px"
        row.style.gap = "15px"
        
        # Container da caixinha de cor editável
        color_container = document.createElement("div")
        color_container.className = "grupo-cor-editavel"
        color_container.style.display = "flex"
        color_container.style.flexDirection = "column"
        color_container.style.alignItems = "center"
        color_container.style.gap = "10px"
        color_container.style.padding = "3px"
        color_container.style.borderRadius = "12px"
        color_container.style.minHeight = "110px"
        color_container.style.transform = "translateY(-6px)"
        
        color_box = document.createElement("input")
        color_box.type = "color"
        color_box.value = cor_hex
        color_box.className = "cor-editavel-bot"
        color_box.style.width = "60px"
        color_box.style.height = "60px"
        color_box.style.minWidth = "60px"
        color_box.style.minHeight = "60px"
        color_box.style.flexShrink = "0"
        color_box.style.cursor = "pointer"
        color_box.style.backgroundColor = "transparent"
        
        color_text = document.createElement("input")
        color_text.type = "text"
        color_text.value = cor_hex.upper()
        color_text.maxLength = 7
        color_text.style.width = "90px"
        color_text.style.background = "transparent"
        color_text.style.border = "none"
        color_text.style.color = PALETA["ui_secundario"]
        color_text.style.fontSize = "16px"
        color_text.style.fontWeight = "600"
        color_text.style.textAlign = "center"
        color_text.style.outline = "none"
        
        nome_cor = buscar_nome_cor(cor_hex, COLOR_DATA)
        name_display = document.createElement("div")
        name_display.innerText = nome_cor
        name_display.style.fontSize = "14px"
        name_display.style.color = PALETA["ui_secundario"]
        name_display.style.marginTop = "-6px"
        name_display.style.textAlign = "center"
        name_display.style.pointerEvents = "none"

        # Escutas de eventos
        def criar_sincronizador(index):
            def sincronizar(e):
                novo_valor = e.target.value.strip()
                if len(novo_valor) == 7 and novo_valor.startswith("#"):
                    elementos_cor[index].value = novo_valor
                    elementos_texto[index].value = novo_valor.upper()
                    gerar_paleta(None)
                else:
                    e.target.value = elementos_texto[index].value.upper()
            return create_proxy(sincronizar)

        proxy_sync = criar_sincronizador(i)
        color_box.addEventListener("change", proxy_sync)
        color_text.addEventListener("change", proxy_sync)
        
        color_container.appendChild(color_box)
        color_container.appendChild(color_text)
        color_container.appendChild(name_display)
        row.appendChild(color_container)

        # Filtra os já usados em colunas ANTERIORES (se aplicável).
        if permite_repetidos:
            candidatos_disponiveis = dados_filtrados
        else:
            candidatos_disponiveis = [
                p for p in dados_filtrados if p["id_base"] not in ids_usados_global
            ]

        if permite_repetidos:
            # Sem regra de duplicidade: os 7 mais próximos, direto.
            top7 = heapq.nsmallest(
                7, candidatos_disponiveis,
                key=lambda p: color_distance(cor_lab, p["color"])
            )
        else:
            # Pega uma "sobra" de candidatos (não só 7) porque cada Pokémon
            # pode aparecer 2x na base (normal + shiny) com cores diferentes.
            # Sem esse buffer, o normal e o shiny do mesmo Pokémon podem os
            # dois cair entre os 7 mais próximos DESTA MESMA coluna, já que
            # ids_usados_global só bloqueia repetição entre colunas diferentes.
            BUFFER_CANDIDATOS = 40
            candidatos_proximos = heapq.nsmallest(
                BUFFER_CANDIDATOS, candidatos_disponiveis,
                key=lambda p: color_distance(cor_lab, p["color"])
            )

            top7 = []
            ids_nesta_coluna = set()
            for p in candidatos_proximos:
                if p["id_base"] in ids_nesta_coluna:
                    continue
                ids_nesta_coluna.add(p["id_base"])
                top7.append(p)
                if len(top7) == 7:
                    break

            # Caso raríssimo: o buffer não tinha 7 IDs únicos (filtros muito
            # restritos). Refaz varrendo tudo, sem limite de buffer.
            if len(top7) < 7 and len(candidatos_disponiveis) > BUFFER_CANDIDATOS:
                top7 = []
                ids_nesta_coluna = set()
                candidatos_completos = sorted(
                    candidatos_disponiveis,
                    key=lambda p: color_distance(cor_lab, p["color"])
                )
                for p in candidatos_completos:
                    if p["id_base"] in ids_nesta_coluna:
                        continue
                    ids_nesta_coluna.add(p["id_base"])
                    top7.append(p)
                    if len(top7) == 7:
                        break

            # Trava esses IDs (já sem duplicatas) para as próximas colunas
            ids_usados_global.update(ids_nesta_coluna)
        
        # Renderização dos cards dos Pokémon
        for pkmn in top7:
            pkmn_box = document.createElement("div")
            pkmn_box.style.display = "flex"
            pkmn_box.style.flexDirection = "column"
            pkmn_box.style.alignItems = "center"
            pkmn_box.style.width = "100px"
            
            id_pokemon = pkmn['id_base']
            sufixo = "_shiny" if "(Shiny)" in pkmn['name'] else ""
            caminho_local = f"./sprites/{id_pokemon}{sufixo}.png"
            
            img = document.createElement("img")
            img.src = caminho_local
            img.style.width = "96px"
            img.style.height = "96px"
            img.style.cursor = "pointer"
            img.style.imageRendering = "pixelated"
            img.title = f"{pkmn['name']} {t('tooltip_clique_salvar')}"
            
            img.onmouseover = lambda e: setattr(e.target.style, "transform", "scale(2.0)")
            img.onmouseout = lambda e: setattr(e.target.style, "transform", "scale(1.0)")
            
            name_tag = document.createElement("span")
            name_tag.innerText = pkmn['name']
            name_tag.style.fontSize = "16px"
            name_tag.style.marginTop = "2px"
            name_tag.style.textAlign = "center"
            name_tag.style.color = PALETA["ui_secundario"] 
            
            pkmn_box.appendChild(img)
            pkmn_box.appendChild(name_tag)
            row.appendChild(pkmn_box)
            
        container.appendChild(row)

def gerar_paleta_aleatoria(event):
    elementos_cor = document.querySelectorAll(".cor-input")
    elementos_texto = document.querySelectorAll(".hex-input")

    for i in range(len(elementos_cor)):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        hex_aleatorio = f"#{r:02X}{g:02X}{b:02X}"
        
        elementos_cor[i].value = hex_aleatorio
        elementos_texto[i].value = hex_aleatorio
    
    gerar_paleta(None)

async def carregar_dados_iniciais():
    global poke_data, COLOR_DATA, BANCO_CORES_PRONTO, PALETA

    # Lê a paleta de cores do CSS antes de tudo, já que gerar_paleta()
    # e as funções de exportação dependem dela pra desenhar textos.
    PALETA = carregar_paleta()

    try:
        response = await pyfetch("pokemon_colors_simple.json")
        if response.status == 200:
            poke_data = await response.json()
            print("Dados dos Pokémon carregados com sucesso!")
            
            # Dispara a geração automática direto, sem loops pesados
            gerar_paleta(None)
    except Exception as e:
        print(f"Erro na inicialização: {e}")

    try:
        resp_cores = await pyfetch("./cores_finais.json")
        COLOR_DATA = await resp_cores.json()

        # Pré-calcula o Lab de cada uma das ~32 mil cores UMA ÚNICA VEZ
        # e manda pro JS, que vai fazer a busca de cor mais próxima nativamente.
        lista_para_js = []
        for hex_key, dados in COLOR_DATA.items():
            if not hex_key.startswith("#"):
                continue
            L, a, b = rgb_to_lab(*parse_input_color(hex_key))
            lista_para_js.append({
                "name": dados.get("name", "Custom Color"),
                "l": L, "a": a, "b": b
            })

        window.prepararBancoCoresJS(lista_para_js)
        BANCO_CORES_PRONTO = True
        print(f"Banco de {len(lista_para_js)} cores preparado no JS.")
    except Exception as e:
        print("Erro ao carregar cores_finais.json:", e)
    gerar_paleta(None)

def exportar_paleta_imagem(event):
    global poke_data
    if not poke_data: return

    elementos_cor = document.querySelectorAll(".cor-input")
    cores_hex = [el.value for el in elementos_cor]

    largura_img = 1100
    espacamento_vertical = 140
    altura_img = 40 + (len(cores_hex) * espacamento_vertical)
    
    img_final = Image.new("RGB", (largura_img, altura_img), PALETA["fundo_imagem"])
    
    draw = ImageDraw.Draw(img_final)
    
    try:
        caminho_fonte = "fonts/VCR_OSD_MONO_1.001.ttf"
        font_hex = ImageFont.truetype(caminho_fonte, size=16)
        font_pkmn = ImageFont.truetype(caminho_fonte, size=16)
    except Exception as e:
        print(f"Erro ao carregar fonte do diretório, usando a padrão: {e}")
        font_hex = ImageFont.load_default()
        font_pkmn = ImageFont.load_default()
    
    y_offset = 40

    for cor_hex in cores_hex:
        cor_lab = rgb_to_lab(*parse_input_color(cor_hex))
        
        draw.rounded_rectangle(
            [40, y_offset, 110, y_offset + 70], 
            radius=8, 
            fill=cor_hex
        )
        draw.text((42, y_offset + 80), cor_hex.upper(), fill=PALETA["texto_secundario"], font=font_hex)
        nome_cor = buscar_nome_cor(cor_hex, COLOR_DATA)
        nome_cor_limpo = remover_acentos_para_imagem(nome_cor)
        linhas_cor = textwrap.wrap(nome_cor_limpo, width=14) 
        
        if len(linhas_cor) >= 2:
            draw.text((42, y_offset + 95), linhas_cor[0], fill=PALETA["texto_terciario"], font=font_hex)
            draw.text((42, y_offset + 110), linhas_cor[1], fill=PALETA["texto_quaternario"], font=font_hex)
        else:
            draw.text((42, y_offset + 95), nome_cor_limpo, fill=PALETA["texto_terciario"], font=font_hex)

        dados_filtrados, permite_repetidos = aplicar_filtros_avancados()
        
        candidatos = sorted(dados_filtrados, key=lambda p: color_distance(cor_lab, p["color"]))
        
        ids_usados = set()
        top7 = []
        for p in candidatos:
            if not permite_repetidos:
                if p["id_base"] in ids_usados:
                    continue
                ids_usados.add(p["id_base"])
                
            top7.append(p)
            if len(top7) == 7: break
            
        x_offset = 160
        largura_sprite = 96

        href_atual = window.location.href.split('?')[0].split('#')[0]
        base_url = href_atual.rsplit('/', 1)[0] if href_atual.endswith('.html') else href_atual.rstrip('/')

        for pkmn in top7:
            try:
                # 1. Identifica o ID e se é Shiny
                id_pokemon = pkmn['id_base']
                sufixo = "_shiny" if "(Shiny)" in pkmn['name'] else ""
                
                # 2. Monta a URL COMPLETA (ex: https://seu-usuario.github.io/repo/sprites/1.png)
                url_sprite_local = f"{base_url}/sprites/{id_pokemon}{sufixo}.png"
                
                # 3. Sistema de Cache
                if url_sprite_local not in SPRITE_CACHE:
                    response = requests.get(url_sprite_local, timeout=5)
                    if response.status_code == 200:
                        SPRITE_CACHE[url_sprite_local] = response.content
                    else:
                        print(f"Sprite não encontrado: {url_sprite_local}")
                        x_offset += 130  # Ajuste crucial: avança o espaço em branco se a imagem falhar
                        continue
                
                # 4. Carrega a imagem direto da memória
                sprite_bytes = SPRITE_CACHE[url_sprite_local]
                sprite_img = Image.open(BytesIO(sprite_bytes)).convert("RGBA")
                sprite_img = sprite_img.resize((largura_sprite, largura_sprite), Image.NEAREST)
                
                img_final.paste(sprite_img, (x_offset, y_offset), sprite_img)
                
                nome_completo = pkmn['name']
                
                # LOGICA DE QUEBRA DE LINHA:
                if " " in nome_completo:
                    partes = nome_completo.split(" ", 1)
                    linha1 = partes[0]
                    linha2 = partes[1]
                    
                    # Centraliza e desenha a primeira linha
                    box1 = draw.textbbox((0, 0), linha1, font=font_pkmn)
                    w1 = box1[2] - box1[0]
                    x_l1 = x_offset + (largura_sprite // 2) - (w1 // 2)
                    draw.text((x_l1, y_offset + 95), linha1, fill=PALETA["texto_primario"], font=font_pkmn)
                    
                    # Centraliza e desenha a segunda linha
                    box2 = draw.textbbox((0, 0), linha2, font=font_pkmn)
                    w2 = box2[2] - box2[0]
                    x_l2 = x_offset + (largura_sprite // 2) - (w2 // 2)
                    draw.text((x_l2, y_offset + 110), linha2, fill=PALETA["texto_terciario"], font=font_pkmn)
                    
                else:
                    # Se não tiver espaço, desenha em linha única
                    text_box = draw.textbbox((0, 0), nome_completo, font=font_pkmn)
                    largura_texto = text_box[2] - text_box[0]
                    x_texto = x_offset + (largura_sprite // 2) - (largura_texto // 2)
                    draw.text((x_texto, y_offset + 95), nome_completo, fill=PALETA["texto_primario"], font=font_pkmn)
                    
            except Exception as e:
                print(f"Erro ao processar {pkmn['name']} na imagem: {e}")
            
            x_offset += 130
            
        y_offset += espacamento_vertical

    try:
        buffered = BytesIO()
        img_final.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        data_url = f"data:image/png;base64,{img_str}"

        # Detecta se o usuário está em um dispositivo iOS (iPhone/iPad)
        is_ios = "iPhone" in window.navigator.userAgent or "iPad" in window.navigator.userAgent

        if is_ios:
            # No iOS, abrimos a imagem em uma nova aba para o usuário salvar nativamente
            nova_aba = window.open("", "_blank")
            if nova_aba:
                # Injeta um HTML limpo com a imagem ocupando a tela e a instrução de salvar
                nova_aba.document.write(f"""
                    <html>
                    <head>
                        <title>{t('ios_titulo_paleta')}</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            body {{ background: {PALETA['fundo_imagem']}; color: {PALETA['texto_secundario']}; margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: sans-serif; text-align: center; padding: 20px; box-sizing: border-box; }}
                            img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin-bottom: 20px; }}
                            p {{ font-size: 14px; letter-spacing: 0.05em; }}
                        </style>
                    </head>
                    <body>
                        <img src="{data_url}" alt="Sua Paleta Pokémon">
                        <p>{t('ios_instrucao')}</p>
                    </body>
                    </html>
                """)
                nova_aba.document.close()
            else:
                # Caso o bloqueador de pop-ups do Safari impeça o window.open
                print("Por favor, permita pop-ups para visualizar e salvar sua imagem.")
        else:
            # Comportamento normal de download direto para Desktop e Android
            a = document.createElement("a")
            a.href = data_url
            a.download = "minha-paleta-pokemon.png"
            a.click()

    except Exception as e:
        print("Erro ao processar download da imagem:", e)

def exportar_paleta_stories(event):
    global poke_data
    if not poke_data: return

    try:
        caminho_fonte = "fonts/VCR_OSD_MONO_1.001.ttf"
        font_hex = ImageFont.truetype(caminho_fonte, size=24)
        font_pkmn = ImageFont.truetype(caminho_fonte, size=20)
        font_titulo = ImageFont.truetype(caminho_fonte, size=36)
    except Exception as e:
        print(f"Erro ao carregar fonte do diretório, usando a padrão: {e}")
        font_hex = ImageFont.load_default()
        font_pkmn = ImageFont.load_default()
        font_titulo = ImageFont.load_default()

    elementos_cor = document.querySelectorAll(".cor-input")
    cores_hex = [el.value for el in elementos_cor]

    # 1. PARÂMETROS DINÂMICOS
    altura_img = 1920
    largura_coluna = 250 
    padding_lateral = 50
    espacamento_entre = 30
    largura_sprite = 160 # Mantendo o sprite maior para Stories
    
    # Cálculo da largura total
    largura_img = (padding_lateral * 2) + (len(cores_hex) * largura_coluna) + ((len(cores_hex) - 1) * espacamento_entre)
    
    img_final = Image.new("RGB", (largura_img, altura_img), PALETA["fundo_imagem"])
    draw = ImageDraw.Draw(img_final)

    # 2. TÍTULO CENTRALIZADO DINAMICAMENTE
    # Calcula o tamanho do texto para centralizar na largura_img
    bbox_titulo = draw.textbbox((0, 0), t('titulo_imagem_horizontal'), font=font_titulo)
    largura_titulo = bbox_titulo[2] - bbox_titulo[0]
    draw.text(((largura_img - largura_titulo) // 2, 100), t('titulo_imagem_horizontal'), fill=PALETA["texto_secundario"], font=font_titulo)
    
    # 3. LOOP DE COLUNAS
    for idx_coluna, cor_hex in enumerate(cores_hex):
        cor_lab = rgb_to_lab(*parse_input_color(cor_hex))
        
        # Calcula X baseado na largura total dinâmica
        x_coluna = padding_lateral + (idx_coluna * (largura_coluna + espacamento_entre))
        
        # Desenha o Bloco de Cor (centralizado dentro da sua coluna de 250px)
        x_rect_start = x_coluna + (largura_coluna // 2) - 80
        draw.rounded_rectangle(
            [x_rect_start, 220, x_rect_start + 160, 340], 
            radius=14, 
            fill=cor_hex
        )
        box_h = draw.textbbox((0, 0), cor_hex.upper(), font=font_hex)
        w_h = box_h[2] - box_h[0]
        x_text_hex = x_coluna + (largura_coluna // 2) - (w_h // 2)
        draw.text((x_text_hex, 355), cor_hex.upper(), fill=PALETA["texto_terciario"], font=font_hex)
        
        nome_cor = buscar_nome_cor(cor_hex, COLOR_DATA)
        nome_cor_limpo = remover_acentos_para_imagem(nome_cor)     
        linhas_cor = textwrap.wrap(nome_cor_limpo, width=16) 
       
        if len(linhas_cor) >= 2:
            b_c1 = draw.textbbox((0, 0), linhas_cor[0], font=font_hex)
            w_c1 = b_c1[2] - b_c1[0]
            x_c1 = x_coluna + (largura_coluna // 2) - (w_c1 // 2)
            draw.text((x_c1, 390), linhas_cor[0], fill=PALETA["texto_terciario"], font=font_hex)
            
            b_c2 = draw.textbbox((0, 0), linhas_cor[1], font=font_hex)
            w_c2 = b_c2[2] - b_c2[0]
            x_c2 = x_coluna + (largura_coluna // 2) - (w_c2 // 2)
            draw.text((x_c2, 415), linhas_cor[1], fill=PALETA["texto_quaternario"], font=font_hex)
        else:
            b_c = draw.textbbox((0, 0), nome_cor_limpo, font=font_hex)
            w_c = b_c[2] - b_c[0]
            x_c = x_coluna + (largura_coluna // 2) - (w_c // 2)
            draw.text((x_c, 390), nome_cor_limpo, fill=PALETA["texto_terciario"], font=font_hex)

        dados_filtrados, permite_repetidos = aplicar_filtros_avancados()

        candidatos = sorted(dados_filtrados, key=lambda p: color_distance(cor_lab, p["color"]))
        
        ids_usados = set()
        top5 = []
        for p in candidatos:
            if not permite_repetidos:
                if p["id_base"] in ids_usados:
                    continue
                ids_usados.add(p["id_base"])           
            top5.append(p)
            if len(top5) == 5: break 
            
        # 2. DESENHA OS 5 POKÉMON EMPILHADOS
        y_pokemon_start = 450     
        espacamento_vertical = 270  

        href_atual = window.location.href.split('?')[0].split('#')[0]
        base_url = href_atual.rsplit('/', 1)[0] if href_atual.endswith('.html') else href_atual.rstrip('/')
        
        for idx_pkmn, pkmn in enumerate(top5):
            try:
                # 1. Identifica o ID e se é Shiny
                id_pokemon = pkmn['id_base']
                sufixo = "_shiny" if "(Shiny)" in pkmn['name'] else ""
                
                # 2. Monta a URL COMPLETA
                url_sprite_local = f"{base_url}/sprites/{id_pokemon}{sufixo}.png"
                
                # 3. Sistema de Cache
                if url_sprite_local not in SPRITE_CACHE:
                    response = requests.get(url_sprite_local, timeout=5)
                    if response.status_code == 200:
                        SPRITE_CACHE[url_sprite_local] = response.content
                    else:
                        print(f"Sprite não encontrado: {url_sprite_local}")
                        continue
                
                # 4. Carrega a imagem direto da memória
                sprite_bytes = SPRITE_CACHE[url_sprite_local]
                sprite_img = Image.open(BytesIO(sprite_bytes)).convert("RGBA")
                sprite_img = sprite_img.resize((largura_sprite, largura_sprite), Image.NEAREST)
                
                # Centraliza o sprite de 160px perfeitamente na coluna
                x_sprite = x_coluna + (largura_coluna // 2) - (largura_sprite // 2)
                y_sprite = y_pokemon_start + (idx_pkmn * espacamento_vertical)
                
                img_final.paste(sprite_img, (x_sprite, y_sprite), sprite_img)
                
                nome_completo = pkmn['name']
                
                # Lógica de quebra de linha ajustada com a variável corrigida (y_sprite)
                if " " in nome_completo:
                    partes = nome_completo.split(" ", 1)
                    linha1 = partes[0]
                    linha2 = partes[1]
                    
                    box1 = draw.textbbox((0, 0), linha1, font=font_pkmn)
                    w1 = box1[2] - box1[0]
                    x_l1 = x_coluna + (largura_coluna // 2) - (w1 // 2)
                    draw.text((x_l1, y_sprite + 165), linha1, fill=PALETA["texto_primario"], font=font_pkmn)
                    
                    box2 = draw.textbbox((0, 0), linha2, font=font_pkmn)
                    w2 = box2[2] - box2[0]
                    x_l2 = x_coluna + (largura_coluna // 2) - (w2 // 2)
                    draw.text((x_l2, y_sprite + 188), linha2, fill=PALETA["texto_terciario"], font=font_pkmn)
                
                else:
                    text_box = draw.textbbox((0, 0), nome_completo, font=font_pkmn)
                    largura_texto = text_box[2] - text_box[0]
                    x_texto = x_coluna + (largura_coluna // 2) - (largura_texto // 2)
                    draw.text((x_texto, y_sprite + 165), nome_completo, fill=PALETA["texto_primario"], font=font_pkmn)
                    
            except Exception as e:
                print(f"Erro ao desenhar coluna {idx_coluna} no Pokémon {pkmn['name']}: {e}")
    # Fluxo de exportação (Web / iOS)
    try:
        buffered = BytesIO()
        img_final.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        data_url = f"data:image/png;base64,{img_str}"

        is_ios = "iPhone" in window.navigator.userAgent or "iPad" in window.navigator.userAgent

        if is_ios:
            nova_aba = window.open("", "_blank")
            if nova_aba:
                nova_aba.document.write(f"""
                    <html>
                    <head>
                        <title>{t('ios_titulo_stories')}</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            body {{ background: {PALETA['fundo_imagem']}; color: {PALETA['texto_secundario']}; margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: sans-serif; text-align: center; padding: 20px; box-sizing: border-box; }}
                            img {{ max-width: 100%; max-height: 85vh; height: auto; border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.6); margin-bottom: 15px; }}
                            p {{ font-size: 14px; letter-spacing: 0.05em; }}
                        </style>
                    </head>
                    <body>
                        <img src="{data_url}" alt="Sua Paleta Pokémon 9:16">
                        <p>{t('ios_instrucao_stories')}</p>
                    </body>
                    </html>
                """)
                nova_aba.document.close()
        else:
            a = document.createElement("a")
            a.href = data_url
            a.download = "minha-paleta-pokemon-stories.png"
            a.click()

    except Exception as e:
        print("Erro ao processar download da imagem vertical:", e)

def exportar_pantone_chart(event):
    global poke_data
    if not poke_data: return

    elementos_cor = document.querySelectorAll(".cor-input")
    cores_hex = [el.value for el in elementos_cor]
    try:
        caminho_fonte = "fonts/VCR_OSD_MONO_1.001.ttf"
        font_hex = ImageFont.truetype(caminho_fonte, size=24)
        font_pkmn = ImageFont.truetype(caminho_fonte, size=20)
        font_titulo = ImageFont.truetype(caminho_fonte, size=36)
    except Exception as e:
        print(f"Erro ao carregar fonte do diretório, usando a padrão: {e}")
        font_hex = ImageFont.load_default()
        font_pkmn = ImageFont.load_default()
        font_titulo = ImageFont.load_default()

    # --- CONFIGURAÇÕES DINÂMICAS ---
    LARGURA_CARD = 500
    ALTURA_CARD = 420
    PADDING = 40
    COLUNAS = 2
    num_cores = len(cores_hex)
    num_linhas = math.ceil(num_cores / COLUNAS)
    
    img_largura = (COLUNAS * LARGURA_CARD) + ((COLUNAS + 1) * PADDING)
    img_altura = (num_linhas * ALTURA_CARD) + ((num_linhas + 1) * PADDING) + 100
    
    img_final = Image.new("RGB", (img_largura, img_altura), PALETA["fundo_imagem"])
    draw = ImageDraw.Draw(img_final)

    draw.text((PADDING, 20), "My Pantone Birth Chart Palette", fill="white", font=font_titulo)

    # --- LOOP DINÂMICO ---
    href_atual = window.location.href.split('?')[0].split('#')[0]
    base_url = href_atual.rsplit('/', 1)[0] if href_atual.endswith('.html') else href_atual.rstrip('/')

    for i, cor_hex in enumerate(cores_hex):
        coluna = i % COLUNAS
        linha = i // COLUNAS
        x_bloco = PADDING + (coluna * (LARGURA_CARD + PADDING))
        y_bloco = 120 + (linha * (ALTURA_CARD + PADDING))
        
        # Desenha o Card
        draw.rectangle([x_bloco, y_bloco, x_bloco + LARGURA_CARD, y_bloco + ALTURA_CARD], fill=cor_hex)
        
        # --- VERIFICAÇÃO DIRETAMENTE NO COLOR_DATA ---
        hex_chave = cor_hex.upper()
        
        # Caso 1: A cor existe no JSON e possui os dados completos de Pantone
        if hex_chave in COLOR_DATA and "code" in COLOR_DATA[hex_chave] and "cat" in COLOR_DATA[hex_chave]:
            info = COLOR_DATA[hex_chave]
            
            draw.text((x_bloco + 20, y_bloco + 20), info['cat'].upper(), fill="white", font=font_pkmn)
            draw.text((x_bloco + 20, y_bloco + 50), info['name'], fill="white", font=font_titulo)
            draw.text((x_bloco + 20, y_bloco + 320), hex_chave, fill="white", font=font_hex)
            draw.text((x_bloco + 20, y_bloco + 350), f"{t('pantone_match_prefixo')}{info['code']}", fill="white", font=font_pkmn)
            
        else:
            # Caso 2: Cor customizada (reaproveita buscar_nome_cor, que já usa
            # cache por hex e delega a busca aproximada pro JS + Quebra de texto)
            nome_aproximado = buscar_nome_cor(cor_hex, COLOR_DATA)

            # Imprime Categoria Fixa
            draw.text((x_bloco + 20, y_bloco + 20), t('categoria_paleta'), fill="white", font=font_pkmn)
            
            # Limpa acentos e aplica a quebra esperta de texto
            import textwrap
            nome_limpo = remover_acentos_para_imagem(nome_aproximado)
            linhas_cor = textwrap.wrap(nome_limpo, width=15)
            
            if len(linhas_cor) >= 2:
                draw.text((x_bloco + 20, y_bloco + 50), linhas_cor[0], fill="white", font=font_titulo)
                draw.text((x_bloco + 20, y_bloco + 95), linhas_cor[1], fill=PALETA["texto_destaque"], font=font_titulo)
            else:
                draw.text((x_bloco + 20, y_bloco + 50), nome_limpo, fill="white", font=font_titulo)
                
            # Imprime apenas o Hex (Sem a linha "Pantone match")
            draw.text((x_bloco + 20, y_bloco + 320), hex_chave, fill="white", font=font_hex)

        # Sprite do Pokémon mais próximo (Mantido igual)
        cor_lab = rgb_to_lab(*parse_input_color(cor_hex))
        dados_filtrados, _ = aplicar_filtros_avancados()
        candidato = sorted(dados_filtrados, key=lambda p: color_distance(cor_lab, p["color"]))[0]
        
        try:
            id_pkmn = candidato['id_base']
            sufixo = "_shiny" if "(Shiny)" in candidato['name'] else ""
            url = f"{base_url}/sprites/{id_pkmn}{sufixo}.png"
            
            if url not in SPRITE_CACHE:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200: SPRITE_CACHE[url] = resp.content
            
            sprite = Image.open(BytesIO(SPRITE_CACHE[url])).convert("RGBA").resize((160, 160), Image.NEAREST)
            img_final.paste(sprite, (x_bloco + 300, y_bloco + 180), sprite)
        except Exception as e:
            print(f"Erro sprite Pantone: {e}")

    # --- EXPORTAÇÃO (Mesma lógica das outras funções) ---
    buffered = BytesIO()
    img_final.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    # Fluxo de exportação (Web / iOS)
    try:
        buffered = BytesIO()
        img_final.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        data_url = f"data:image/png;base64,{img_str}"

        is_ios = "iPhone" in window.navigator.userAgent or "iPad" in window.navigator.userAgent

        if is_ios:
            nova_aba = window.open("", "_blank")
            if nova_aba:
                nova_aba.document.write(f"""
                    <html>
                    <head>
                        <title>{t('ios_titulo_moodboard')}</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            body {{ background: {PALETA['fundo_imagem']}; color: {PALETA['texto_secundario']}; margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: sans-serif; text-align: center; padding: 20px; box-sizing: border-box; }}
                            img {{ max-width: 100%; max-height: 85vh; height: auto; border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.6); margin-bottom: 15px; }}
                            p {{ font-size: 14px; letter-spacing: 0.05em; }}
                        </style>
                    </head>
                    <body>
                        <img src="{data_url}" alt="Sua Moodboard Pokémon 9:16">
                        <p>{t('ios_instrucao')}</p>
                    </body>
                    </html>
                """)
                nova_aba.document.close()
        else:
            a = document.createElement("a")
            a.href = data_url
            a.download = "meu-moodboard-pokemon.png"
            a.click()

    except Exception as e:
        print("Erro ao processar download de moodboard:", e)

def fechar_filtros_e_gerar(event=None):
    global FILTROS_SUJOS
    FILTROS_SUJOS = True  # os checkboxes podem ter mudado, força reprocessar
    gerar_paleta(event)

asyncio.ensure_future(carregar_dados_iniciais())
document.getElementById("btn-fechar-filtros").onclick = create_proxy(fechar_filtros_e_gerar)
proxy_gerar = create_proxy(gerar_paleta)

def atualizar_tela(event):
    window.setTimeout(proxy_gerar, 10)

proxy_atualizar = create_proxy(atualizar_tela)
proxy_moodboard = create_proxy(exportar_pantone_chart)
proxy_paleta = create_proxy(exportar_paleta_imagem)
proxy_stories = create_proxy(exportar_paleta_stories)
proxy_aleatorio = create_proxy(gerar_paleta_aleatoria)
document.getElementById("lista-cores").addEventListener("input", proxy_atualizar)
document.getElementById("btn-add-cor").addEventListener("click", proxy_atualizar)
document.getElementById("btn-exportar_pantone_chart").addEventListener("click", proxy_moodboard)
document.querySelector("#btn-exportar").addEventListener("click", proxy_paleta)
document.querySelector("#btn-stories").addEventListener("click", proxy_stories)
document.querySelector("#btn-aleatorio").addEventListener("click", proxy_aleatorio)