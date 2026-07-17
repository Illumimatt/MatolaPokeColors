import math
import random
import asyncio
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
        row.appendChild(color_box)
        
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

asyncio.ensure_future(carregar_dados_iniciais())

document.querySelector("#btn-aleatorio").addEventListener("click", create_proxy(gerar_paleta_aleatoria))