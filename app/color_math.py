"""Matemática de cor: conversão RGB -> CIE Lab e distância perceptual entre
cores.

Sem NENHUMA dependência de DOM/JS -- é só matemática. Isso é proposital:
mantém essa peça 100% testável com Python puro (fora do navegador), o que
não era possível antes, com tudo misturado num só app.py acoplado ao Pyodide.
"""
import math


def parse_input_color(hex_color):
    """'#RRGGBB' -> [r, g, b] (cada canal 0-255)."""
    hex_color = hex_color.strip().replace("#", "")
    return [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]


def rgb_to_lab(r, g, b):
    r, g, b = r / 255.0, g / 255.0, b / 255.0

    def gamma(c):
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92

    r, g, b = gamma(r), gamma(g), gamma(b)

    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) * 100
    y = (r * 0.2126 + g * 0.7152 + b * 0.0722) * 100
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) * 100

    x /= 95.047
    y /= 100.000
    z /= 108.883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    fx, fy, fz = f(x), f(y), f(z)

    L = 116 * fy - 16
    a = 500 * (fx - fy)
    b = 200 * (fy - fz)
    return [L, a, b]


def hex_to_lab(hex_color):
    """Atalho: '#RRGGBB' -> Lab, numa chamada só.

    O código original repetia `rgb_to_lab(*parse_input_color(cor_hex))` em
    mais de meia dúzia de lugares -- esse atalho existe só pra eliminar
    essa repetição.
    """
    return rgb_to_lab(*parse_input_color(hex_color))


def color_distance(lab1, lab2):
    """Distância euclidiana simples no espaço Lab (Delta E CIE76)."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))
