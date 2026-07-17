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
            
            img = document.createElement("img")
            img.src = pkmn['sprite']
            img.style.width = "96px"
            img.style.height = "96px"
            img.style.cursor = "pointer"
            img.style.imageRendering = "pixelated"
            img.title = f"{pkmn['name']} (Click para salvar)"
            img.onmouseover = lambda e: setattr(e.target.style, "transform", "scale(2.0)")
            img.onmouseout = lambda e: setattr(e.target.style, "transform", "scale(1.0)")
            
            name_tag = document.createElement("span")
            name_tag.innerText = pkmn['name'].capitalize()
            name_tag.style.fontSize = "11px"
            name_tag.style.marginTop = "2px"
            name_tag.style.textAlign = "center"
            name_tag.style.color = "#333"
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
    GIST_URL = "https://gist.githubusercontent.com/Illumimatt/d5dfddb18337f4e365ef688826c57206/raw/934816b3310b73ecc5ebe870af0fb7a73aa7ec05/gistfile1.txt"
    try:
        response = await pyfetch(GIST_URL)
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
        font_hex = ImageFont.load_default(size=16)
        font_pkmn = ImageFont.load_default(size=11)
    except:
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

        for pkmn in top7:
            try:
                response = requests.get(pkmn['sprite'])
                if response.status_code == 200:
                    sprite_img = Image.open(BytesIO(response.content)).convert("RGBA")
                    sprite_img = sprite_img.resize((largura_sprite, largura_sprite), Image.NEAREST)
                    img_final.paste(sprite_img, (x_offset, y_offset), sprite_img)
                    
                    nome_completo = pkmn['name'].capitalize()
                    
                    # LOGICA DE QUEBRA DE LINHA:
                    # Se houver um espaço no nome (ex: "Basculin blue"), separamos em duas linhas
                    if " " in nome_completo:
                        partes = nome_completo.split(" ", 1)
                        linha1 = partes[0]
                        linha2 = partes[1]
                        
                        # Centraliza e desenha a primeira linha (Nome principal)
                        box1 = draw.textbbox((0, 0), linha1, font=font_pkmn)
                        w1 = box1[2] - box1[0]
                        x_l1 = x_offset + (largura_sprite // 2) - (w1 // 2)
                        draw.text((x_l1, y_offset + 95), linha1, fill="#FFFFF0", font=font_pkmn)
                        
                        # Centraliza e desenha a segunda linha (Variação/Forma) logo abaixo
                        box2 = draw.textbbox((0, 0), linha2, font=font_pkmn)
                        w2 = box2[2] - box2[0]
                        x_l2 = x_offset + (largura_sprite // 2) - (w2 // 2)
                        draw.text((x_l2, y_offset + 110), linha2, fill="#94a3b8", font=font_pkmn) # Tom cinza discreto para o "subtítulo"
                    
                    else:
                        # Se não tiver espaço, desenha em linha única normalmente
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

document.querySelector("#btn-exportar").addEventListener("click", create_proxy(exportar_paleta_imagem))        

asyncio.ensure_future(carregar_dados_iniciais())

document.querySelector("#btn-aleatorio").addEventListener("click", create_proxy(gerar_paleta_aleatoria))