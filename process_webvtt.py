import argparse
from typing import List
import glob
import os
import helpers.logging
import helpers.postprocess
import helpers.preprocess


def main():
    parser = argparse.ArgumentParser(description="Process .webvtt files.")
    parser.add_argument(
        "path", help="Path to the file, or folder containing .webvtt files"
    )
    parser.add_argument(
        "action", help="What to do with the files", choices={"prepare", "finalize"}
    )
    args = parser.parse_args()
    log = helpers.logging.create_log(args.action)
    path = args.path
    log.info("Starting", action=args.action, path=path)
    files: List[str] = []
    if os.path.isfile(path):
        files.append(path)
    elif os.path.isdir(path):
        pattern = os.path.join(path, "**", "*.webvtt")
        files.extend(glob.glob(pattern, recursive=True))
    else:
        log.exception("Invalid path", path=path)
        raise Exception(f"Path {path} is not valid.")
    if args.action == "prepare":
        for vtt_file in files:
            helpers.preprocess.process_vtt(vtt_file, log)
    if args.action == "finalize":
        for vtt_file in files:
            helpers.postprocess.process_vtt(vtt_file, log)
    log.info("Done.")


if __name__ == "__main__":
    main()
