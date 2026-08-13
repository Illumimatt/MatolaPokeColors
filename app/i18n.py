"""Internacionalização (i18n).

Fonte única de verdade: o dicionário TRADUCOES mora em script.js. Este
módulo só consulta via window.t() -- não duplica o dicionário aqui, então
um texto novo adicionado em script.js já fica disponível pro Python de
graça, sem precisar traduzir em dois lugares.
"""
from js import window


def t(chave):
    """Traduz uma chave usando o idioma ativo (detectado em script.js)."""
    try:
        return window.t(chave)
    except Exception as e:
        print(f"Erro ao traduzir chave '{chave}': {e}")
        return chave
