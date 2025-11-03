import webvtt
import re
import glob
import os
import argparse


def process_vtt(file):
    all_caps: bool = True
    newline_in_previous: bool = False
    with open(f"{file}.vtt", "w", encoding="utf-8") as f:
        for caption in webvtt.read(file):
            if re.search(r"[a-z]", caption.text):
                all_caps = False
            fragment: str = ""
            fragment += f"⎡⎡{caption.start} --> {caption.end}⎦⎦ "
            # multiple speakers
            if caption.raw_text.startswith("-"):
                fragment += (
                    "\n".join(
                        re.sub(r"^-(\s*[A-Z]+:)?", r"⎡⎡Speaker \1⎦⎦ ", line)
                        for line in caption.lines
                    )
                    + " "
                )
            else:
                cue_text = " ".join(caption.raw_text.splitlines()) + " "
                fragment += re.sub(r"^([A-Z]+:)", r"⎡⎡Speaker \1⎦⎦ ", cue_text)
            # sounds in brackets
            if re.match(r"^\[[^\]]*\]$", caption.raw_text) or re.match(
                r"⎡⎡Speaker[^⎦]*?⎦⎦ *\[[^\]]*\]", caption.raw_text
            ):
                if newline_in_previous:
                    fragment += "\n"
                else:
                    fragment = "\n" + fragment + "\n"
                newline_in_previous = True
            elif fragment.endswith("] "):
                fragment += "\n"
                newline_in_previous = True
            # break after punctuation
            elif re.search(r"[!?\.]$", caption.text):
                fragment += "\n"
                newline_in_previous = True
            else:
                newline_in_previous = False
            f.write(re.sub(" +", " ", fragment))

    if all_caps:
        print("All captions are in uppercase.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process all .webvtt files in a folder."
    )
    parser.add_argument("folder", help="Path to the folder containing .webvtt files")
    args = parser.parse_args()

    folder = args.folder
    pattern = os.path.join(folder, "**", "*.webvtt")
    for vtt_file in glob.glob(pattern, recursive=True):
        process_vtt(vtt_file)
