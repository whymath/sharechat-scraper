import googletrans
from googletrans import Translator

def initialize_translator():
    return Translator()

def translate_text(text, translator):
    return translator.translate(text).text
