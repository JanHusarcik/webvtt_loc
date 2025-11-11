import webvtt
import re
import random
import unicodedata

def random_unicode_text(text: str) -> str:
    # Build a list of all Latin letters in the range U+0041 to U+017F
    latin_letters = [
        chr(cp)
        for cp in range(0x41, 0x180)
        if unicodedata.category(chr(cp)).startswith('L')
    ]
    def repl(match):
        return random.choice(latin_letters)
    return re.sub(r"\w", repl, text)



def main():
    input_path = r"d:\work\memsource\nbc\orig_from_gdrive\FlippingExes\FlippingExes_Q7L01_S01_E01_CCA_en-US.webvtt"
    output_path = r"d:\coding\webvtt_loc\tests\sample3.webvtt"

    vtt = webvtt.read(input_path)
    for cue in vtt.captions:
        cue.text = random_unicode_text(cue.text)
    vtt.save(output_path)
    print(f"Sanitized WebVTT saved to {output_path}")


if __name__ == "__main__":
    main()
