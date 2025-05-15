import arabic_reshaper
from bidi.algorithm import get_display

# Example function to reshape and fix Arabic text direction
def fix_arabic_text(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)
