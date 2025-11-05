import webvtt
import re
from structlog import BoundLogger
import os


def process_vtt(file: str, log: BoundLogger):
    all_caps: bool = True
    cue_count: int = 0
    newline_in_previous: bool = False
    log.info("Processing file", file=file)
    try:
        # Prepare output path in 'prepared' subfolder
        orig_dir = os.path.dirname(file)
        orig_filename = os.path.basename(file)
        prepared_dir = os.path.join(orig_dir, "prepared")
        os.makedirs(prepared_dir, exist_ok=True)
        out_path = os.path.join(prepared_dir, orig_filename)

        with open(out_path, "w", encoding="utf-8") as f:
            for caption in webvtt.read(file):
                if re.search(r"[a-z]", caption.text):
                    all_caps = False
                fragment: str = ""
                fragment += f"⎡⎡{caption.start} --> {caption.end}⎦⎦ "
                # multiple speakers
                if caption.raw_text.startswith("-") and not caption.raw_text.startswith(
                    "--"
                ):
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
                elif re.search(r"[!?\.][\"']?$", caption.text):
                    fragment += "\n"
                    newline_in_previous = True
                else:
                    newline_in_previous = False
                f.write(re.sub(" +", " ", fragment))
                cue_count += 1
    except Exception as e:
        log.exception("Processing error", file=file, error=str(e))
        raise Exception("Processing error") from e
    log.info("File processed", cues=cue_count)
    if all_caps:
        print("All captions are in uppercase.")
