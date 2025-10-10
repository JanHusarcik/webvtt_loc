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
            if re.search(r'[a-z]', caption.text):
                all_caps = False
            fragment: str = ""
            fragment += f"⎡⎡{caption.start} --> {caption.end}⎦⎦ "
            if caption.raw_text.startswith("- "):
                fragment += caption.raw_text + " "
            else:
                fragment += " ".join(caption.raw_text.splitlines()) + " "
            if re.match(r"^\[.*\]$", caption.raw_text):
                if newline_in_previous:
                    fragment = fragment+"\n"
                else:
                    fragment = "\n"+fragment+"\n"
                newline_in_previous = True
            elif re.search(r"[!?\.]$", caption.text):
                fragment += "\n"
                newline_in_previous = True
            else:
                newline_in_previous = False
            f.write(re.sub(" +", " ", fragment))

    if all_caps:
        print("All captions are in uppercase.")


for vtt_file in glob.glob("**/*.webvtt", recursive=True):
    process_vtt(vtt_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process all .webvtt files in a folder.")
    parser.add_argument("folder", help="Path to the folder containing .webvtt files")
    args = parser.parse_args()

    folder = args.folder
    pattern = os.path.join(folder, "**", "*.webvtt")
    for vtt_file in glob.glob(pattern, recursive=True):
        process_vtt(vtt_file)