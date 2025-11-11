import webvtt
import os
import re
from typing import List, Final
from structlog import BoundLogger
import textwrap

LINE_LENGTH: Final[int] = 36
TIMESTAMP_PATTERN: Final[str] = r"(⎡⎡\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}⎦⎦)"


def wrap_text_lines(text: str, width: int) -> list[str]:
    """
    Wrap text into lines without breaking words.
    """
    lines_out = []
    for para in text.splitlines():
        if not para.strip():
            lines_out.append("")  # preserve blank lines
            continue
        wrapped = textwrap.wrap(
            para,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
            replace_whitespace=True,
            drop_whitespace=True,
        )
        lines_out.extend(wrapped)
    return lines_out


def parse_vtt_line(line: str) -> webvtt.Caption:
    # Regex to extract timestamp
    timestamp_re = re.compile(
        r"⎡⎡(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})⎦⎦"
    )
    # Regex to match speaker tags
    speaker_re = re.compile(r"⎡⎡Speaker (?:([^:⎦]+):?)?⎦⎦")

    # Extract timestamp
    ts_match = timestamp_re.match(line)
    if not ts_match:
        raise ValueError("No timestamp found in line")

    start, end = ts_match.group(1), ts_match.group(2)
    text = line[ts_match.end() :].strip()

    # Find all speaker tags to determine if there is only one unique speaker
    speakers = []
    for m in speaker_re.finditer(text):
        name = m.group(1)
        if name:
            speakers.append(name.strip())
        else:
            speakers.append("")  # anonymous speaker

    # Split text into caption lines, one per speaker tag
    lines = []
    matches = list(speaker_re.finditer(text))
    # Handle text before the first speaker tag
    if matches:
        first_start = matches[0].start()
        pre_text = text[:first_start].strip()
        if pre_text:
            lines.append(pre_text)
    # Handle each speaker tag and its content
    for idx, m in enumerate(matches):
        start_idx = m.end()
        next_m = matches[idx + 1] if idx + 1 < len(matches) else None
        end_idx = next_m.start() if next_m else len(text)
        content = text[start_idx:end_idx].strip()
        name = m.group(1)
        if len(speakers) == 1:
            line_text = f"{name + ': ' if name else '- '}{content}".strip()
        else:
            if name:
                line_text = f"- {name}: {content}".strip()
            else:
                line_text = f"- {content}".strip()
        lines.append(line_text)


    # If there are no speaker tags, just use the text as is
    if not lines:
        lines = [text]

    # Wrap each line if it exceeds LINE_LENGTH
    wrapped_lines = []
    for line in lines:
        if len(line) > LINE_LENGTH:
            wrapped_lines.extend(wrap_text_lines(line, LINE_LENGTH))
        else:
            wrapped_lines.append(line)

    caption_text = "\n".join(wrapped_lines)

    return webvtt.Caption(start, end, caption_text)

def process_line(line: str, result: list) -> None:
    matches = list(re.finditer(TIMESTAMP_PATTERN, line))
    if not matches:
        # No timestamp: append to previous
        if result:
            result[-1] += " " + line
        else:
            result.append(line)
    elif len(matches) == 1 and matches[0].start() == 0:
        # Single timestamp at start: start new item
        result.append(line)
    else:
        # Multiple timestamps: split at each timestamp, including any content before the first timestamp
        splits = [0] + [m.start() for m in matches] + [len(line)]
        for i in range(len(splits) - 1):
            segment = line[splits[i]:splits[i + 1]].strip()
            if not segment:
                continue
            # If this is the first segment and it does not start with a timestamp, join it to previous
            if i == 0 and not re.match(TIMESTAMP_PATTERN, segment):
                if result:
                    result[-1] += " " + segment
                else:
                    result.append(segment)
            else:
                result.append(segment)


def read_file(file: str) -> List[str]:
    result = []
    with open(file, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")
            if not line.strip():
                continue 
            process_line(line, result)
    return result



def process_vtt(file: str, log: BoundLogger):
    log.info("Processing file", file=file)
    vtt = webvtt.WebVTT()
    try:
        lines = read_file(file)
        for line in lines:
            caption = parse_vtt_line(line)
            vtt.captions.append(caption)
        # Create 'final' subfolder path
        orig_dir = os.path.dirname(file)
        orig_filename = os.path.basename(file)
        final_dir = os.path.join(orig_dir, "final")
        os.makedirs(final_dir, exist_ok=True)
        out_path = os.path.join(final_dir, orig_filename)
        vtt.save(out_path)
    except Exception as e:
        log.exception("Processing error", file=file, error=str(e))
        raise Exception("Processing error") from e
    log.info("File processed")
