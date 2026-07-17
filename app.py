from PIL import Image
from io import BytesIO
from js import window, document
import base64
import math
import random
import asyncio
import requests
from pyodide.http import pyfetch
from pyodide.ffi import create_proxy
from pyscript import document

# --- VARIÁVEL GLOBAL PARA GUARDAR OS DADOS ---
SPRITE_CACHE = {}
poke_data = []

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


# --- Sincronização e Validação do Input ---
def handle_hex_input(event):
    idx = event.target.id[3:]
    val = event.target.value.strip()
    
    if val.startswith('#'):
        val = val[1:]
        
    val = "".join([c for c in val if c.isalnum()])[:6]
    
    if val:
        event.target.value = f"#{val}"
    else:
        event.target.value = ""
        
    if len(val) == 6:
        try:
            int(val, 16)
            document.querySelector(f"#c{idx}").value = f"#{val}"
            gerar_paleta(None)
        except ValueError:
            pass

def sync_hex_from_picker(event):
    idx = event.target.id[1:]
    document.querySelector(f"#hex{idx}").value = event.target.value
    gerar_paleta(None)

for i in range(1, 5):
    document.querySelector(f"#hex{i}").addEventListener("input", create_proxy(handle_hex_input))
    document.querySelector(f"#c{i}").addEventListener("input", create_proxy(sync_hex_from_picker))

# --- FUNÇÃO PRINCIPAL DE GERAR PALETA ---
def gerar_paleta(event):
    global poke_data
    if not poke_data:
        print("Os dados dos Pokémon ainda estão sendo carregados. Aguarde um instante...")
        return

    cores_hex = []
    for i in range(1, 5):
        val_txt = document.querySelector(f"#hex{i}").value.strip()
        if val_txt and val_txt.startswith('#'):
            cores_hex.append(val_txt)
        else:
            cores_hex.append(document.querySelector(f"#c{i}").value)

    container = document.querySelector("#output-container")
    container.innerHTML = "" 
    
    ids_usados = set()

    for cor_hex in cores_hex:
        cor_lab = rgb_to_lab(*parse_input_color(cor_hex))
        
        row = document.createElement("div")
        row.className = "color-row"
        row.style.display = "flex"
        row.style.alignItems = "center"
        row.style.marginBottom = "5px"
        row.style.gap = "15px"
        
        color_box = document.createElement("div")
        color_box.style.width = "60px"
        color_box.style.height = "60px"
        color_box.style.backgroundColor = cor_hex
        color_box.style.borderRadius = "8px"
        
        color_container = document.createElement("div")
        color_container.style.display = "flex"
        color_container.style.flexDirection = "column"
        color_container.style.alignItems = "center"
        color_container.style.gap = "6px"
        
        color_text = document.createElement("span")
        color_text.innerText = cor_hex.upper()
        color_text.style.fontSize = "12px"
        color_text.style.fontWeight = "600"
        color_text.style.color = "#cbd5e1" 

        color_container.appendChild(color_box)
        color_container.appendChild(color_text)
        
        row.appendChild(color_container)
        
        candidatos = sorted(poke_data, key=lambda p: color_distance(cor_lab, p["color"]))
        top7 = []
        for p in candidatos:
            if p["id_base"] not in ids_usados:
                ids_usados.add(p["id_base"])
                top7.append(p)
            if len(top7) == 7: break
        
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
            img.title = f"{pkmn['name']} (Click para salvar)"
            
            img.onmouseover = lambda e: setattr(e.target.style, "transform", "scale(2.0)")
            img.onmouseout = lambda e: setattr(e.target.style, "transform", "scale(1.0)")
            
            nome_limpo = pkmn['name'].replace(" (Shiny)", "").capitalize()
            
            name_tag = document.createElement("span")
            name_tag.innerText = nome_limpo
            name_tag.style.fontSize = "11px"
            name_tag.style.marginTop = "2px"
            name_tag.style.textAlign = "center"
            name_tag.style.color = "#cbd5e1" 
            name_tag.style.fontFamily = "sans-serif"
            
            pkmn_box.appendChild(img)
            pkmn_box.appendChild(name_tag)
            row.appendChild(pkmn_box)
            
        container.appendChild(row)

def gerar_paleta_aleatoria(event):
    for i in range(1, 5):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        hex_aleatorio = f"#{r:02X}{g:02X}{b:02X}"
        
        document.querySelector(f"#c{i}").value = hex_aleatorio
        document.querySelector(f"#hex{i}").value = hex_aleatorio
        
    gerar_paleta(None)

async def carregar_dados_iniciais():
    global poke_data
    ARQUIVO_JSON = "./pokemon_colors_simple.json"
    
    try:
        response = await pyfetch(ARQUIVO_JSON)
        poke_data = await response.json()
        
        gerar_paleta(None)
        
    except Exception as e:
        print("Erro ao carregar o JSON inicial:", e)

def exportar_paleta_imagem(event):
    global poke_data
    if not poke_data: return

    cores_hex = []
    for i in range(1, 5):
        val_txt = document.querySelector(f"#hex{i}").value.strip()
        if val_txt and val_txt.startswith('#'):
            cores_hex.append(val_txt)
        else:
            cores_hex.append(document.querySelector(f"#c{i}").value)

    largura_img = 1100
    altura_img = 620 # Aumentamos um pouquinho a altura para acomodar a segunda linha de texto
    img_final = Image.new("RGB", (largura_img, altura_img), "#1b1b1b")
    
    from PIL import ImageDraw, ImageFont
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
    espacamento_linhas = 140 # Aumentamos o espaçamento vertical entre os cards por conta da quebra de linha

    for cor_hex in cores_hex:
        cor_lab = rgb_to_lab(*parse_input_color(cor_hex))
        
        draw.rounded_rectangle(
            [40, y_offset, 110, y_offset + 70], 
            radius=8, 
            fill=cor_hex
        )
        draw.text((42, y_offset + 80), cor_hex.upper(), fill="#cbd5e1", font=font_hex)
        
        candidatos = sorted(poke_data, key=lambda p: color_distance(cor_lab, p["color"]))
        ids_usados = set()
        top7 = []
        for p in candidatos:
            if p["id_base"] not in ids_usados:
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
                
                # Opcional: Remove a tag (Shiny) do texto para a imagem ficar mais limpa
                nome_completo = pkmn['name'].replace(" (Shiny)", "").capitalize()
                
                # LOGICA DE QUEBRA DE LINHA:
                if " " in nome_completo:
                    partes = nome_completo.split(" ", 1)
                    linha1 = partes[0]
                    linha2 = partes[1]
                    
                    # Centraliza e desenha a primeira linha
                    box1 = draw.textbbox((0, 0), linha1, font=font_pkmn)
                    w1 = box1[2] - box1[0]
                    x_l1 = x_offset + (largura_sprite // 2) - (w1 // 2)
                    draw.text((x_l1, y_offset + 95), linha1, fill="#FFFFF0", font=font_pkmn)
                    
                    # Centraliza e desenha a segunda linha
                    box2 = draw.textbbox((0, 0), linha2, font=font_pkmn)
                    w2 = box2[2] - box2[0]
                    x_l2 = x_offset + (largura_sprite // 2) - (w2 // 2)
                    draw.text((x_l2, y_offset + 110), linha2, fill="#94a3b8", font=font_pkmn)
                    
                else:
                    # Se não tiver espaço, desenha em linha única
                    text_box = draw.textbbox((0, 0), nome_completo, font=font_pkmn)
                    largura_texto = text_box[2] - text_box[0]
                    x_texto = x_offset + (largura_sprite // 2) - (largura_texto // 2)
                    draw.text((x_texto, y_offset + 95), nome_completo, fill="#FFFFF0", font=font_pkmn)
                    
            except Exception as e:
                print(f"Erro ao processar {pkmn['name']} na imagem: {e}")
            
            x_offset += 130
            
        y_offset += espacamento_linhas

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
                        <title>Salvar Paleta</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            body {{ background: #1b1b1b; color: #cbd5e1; margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: sans-serif; text-align: center; padding: 20px; box-sizing: border-box; }}
                            img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin-bottom: 20px; }}
                            p {{ font-size: 14px; letter-spacing: 0.05em; }}
                        </style>
                    </head>
                    <body>
                        <img src="{data_url}" alt="Sua Paleta Pokémon">
                        <p>👆 Pressione e segure na imagem para "Adicionar às Fotos" 📸</p>
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

    cores_hex = []
    for i in range(1, 5):
        val_txt = document.querySelector(f"#hex{i}").value.strip()
        if val_txt and val_txt.startswith('#'):
            cores_hex.append(val_txt)
        else:
            cores_hex.append(document.querySelector(f"#c{i}").value)

    # 1. RESOLUÇÃO PADRÃO STORIES: 1080 x 1920 pixels (Vertical)
    largura_img = 1080
    altura_img = 1920
    img_final = Image.new("RGB", (largura_img, altura_img), "#1b1b1b")
    
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img_final)
    
    try:
        caminho_fonte = "fonts/VCR_OSD_MONO_1.001.ttf"

        font_titulo = ImageFont.truetype(caminho_fonte, size=46)
        font_hex = ImageFont.truetype(caminho_fonte, size=24)
        font_pkmn = ImageFont.truetype(caminho_fonte, size=24)
    except Exception as e:
        print(f"Erro ao carregar fonte do diretório, usando a padrão: {e}")
        font_titulo = ImageFont.load_default()
        font_hex = ImageFont.load_default()
        font_pkmn = ImageFont.load_default()
        
    # Título principal no topo
    draw.text((60, 100), "MINHA PALETA POKÉMON", fill="#cbd5e1", font=font_titulo)
    
    # MATEMÁTICA DAS COLUNAS (Ajustada para sprites maiores)
    largura_util = 1080 - 100  # 980px livres (Margens de 50px nas laterais)
    largura_coluna = 220       # Coluna ligeiramente maior para o sprite de 160px
    espacamento_coluna = (largura_util - (4 * largura_coluna)) // 3
    
    # O DOBRO DO TAMANHO: Pula de 96px para 160px (preserva proporção e foca no mobile)
    largura_sprite = 160

    for idx_coluna, cor_hex in enumerate(cores_hex):
        cor_lab = rgb_to_lab(*parse_input_color(cor_hex))
        
        # Posição X da coluna
        x_coluna = 50 + idx_coluna * (largura_coluna + espacamento_coluna)
        
        # 1. DESENHA OS BLOCOS DE CORES NO TOPO
        x_rect_start = x_coluna + (largura_coluna // 2) - 80
        x_rect_end = x_rect_start + 160
        draw.rounded_rectangle(
            [x_rect_start, 220, x_rect_end, 340], 
            radius=14, 
            fill=cor_hex
        )
        
        box_h = draw.textbbox((0, 0), cor_hex.upper(), font=font_hex)
        w_h = box_h[2] - box_h[0]
        x_text_hex = x_coluna + (largura_coluna // 2) - (w_h // 2)
        draw.text((x_text_hex, 355), cor_hex.upper(), fill="#94a3b8", font=font_hex)
        
        # Busca os candidatos próximos
        candidatos = sorted(poke_data, key=lambda p: color_distance(cor_lab, p["color"]))
        ids_usados = set()
        top5 = []  # ALTERADO: Limite para 5 Pokémon
        for p in candidatos:
            if p["id_base"] not in ids_usados:
                ids_usados.add(p["id_base"])
                top5.append(p)
            if len(top5) == 5: break
            
        # 2. DESENHA OS 5 POKÉMON EMPILHADOS
        y_pokemon_start = 450      # Ponto de partida vertical
        espacamento_vertical = 270  # Mais espaço vertical para acomodar o sprite gigante + texto

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
                
                # Remove a tag (Shiny) do texto para a imagem ficar mais limpa
                nome_completo = pkmn['name'].replace(" (Shiny)", "").capitalize()
                
                # Lógica de quebra de linha ajustada com a variável corrigida (y_sprite)
                if " " in nome_completo:
                    partes = nome_completo.split(" ", 1)
                    linha1 = partes[0]
                    linha2 = partes[1]
                    
                    box1 = draw.textbbox((0, 0), linha1, font=font_pkmn)
                    w1 = box1[2] - box1[0]
                    x_l1 = x_coluna + (largura_coluna // 2) - (w1 // 2)
                    draw.text((x_l1, y_sprite + 155), linha1, fill="#FFFFF0", font=font_pkmn)
                    
                    box2 = draw.textbbox((0, 0), linha2, font=font_pkmn)
                    w2 = box2[2] - box2[0]
                    x_l2 = x_coluna + (largura_coluna // 2) - (w2 // 2)
                    draw.text((x_l2, y_sprite + 178), linha2, fill="#94a3b8", font=font_pkmn)
                
                else:
                    text_box = draw.textbbox((0, 0), nome_completo, font=font_pkmn)
                    largura_texto = text_box[2] - text_box[0]
                    x_texto = x_coluna + (largura_coluna // 2) - (largura_texto // 2)
                    draw.text((x_texto, y_sprite + 155), nome_completo, fill="#FFFFF0", font=font_pkmn)
                    
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
                        <title>Salvar Paleta Stories</title>
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <style>
                            body {{ background: #1b1b1b; color: #cbd5e1; margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; font-family: sans-serif; text-align: center; padding: 20px; box-sizing: border-box; }}
                            img {{ max-width: 100%; max-height: 85vh; height: auto; border-radius: 12px; box-shadow: 0 6px 15px rgba(0,0,0,0.6); margin-bottom: 15px; }}
                            p {{ font-size: 14px; letter-spacing: 0.05em; }}
                        </style>
                    </head>
                    <body>
                        <img src="{data_url}" alt="Sua Paleta Pokémon 9:16">
                        <p>👆 Pressione e segure na imagem para "Adicionar às Fotos" e postar nos Stories! 📸</p>
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

asyncio.ensure_future(carregar_dados_iniciais())
document.querySelector("#btn-exportar").addEventListener("click", create_proxy(exportar_paleta_imagem))    
document.querySelector("#btn-stories").addEventListener("click", create_proxy(exportar_paleta_stories))       
document.querySelector("#btn-aleatorio").addEventListener("click", create_proxy(gerar_paleta_aleatoria))