# preprocess_webvtt.py

A utility script to process all `.webvtt` subtitle files in a specified folder, transforming their content and saving the results as new `.vtt` files.

## Features

- Recursively finds all `.webvtt` files in a given directory.
- Processes each caption:
  - Adds a custom timestamp marker.
  - Joins multi-line captions.
  - Handles speaker lines and special formatting.
  - Detects if all captions are uppercase.
- Outputs processed captions to new files with a `.vtt` extension (e.g., `input.webvtt` → `input.webvtt.vtt`).

## Requirements

- [uv](https://docs.astral.sh/uv/)


## Usage

```
uv run preprocess_webvtt.py /path/to/folder
```


- Replace `path\to\folder` with the directory containing your `.webvtt` files.
- The script will process all `.webvtt` files found recursively in the folder.

## Output

- For each input file `filename.webvtt`, a processed file `filename.webvtt.vtt` will be created in the same directory.
- If all captions in a file are uppercase, a message will be printed to the console.

## Example

```
uv run preprocess_webvtt.py c:\subtitles
```

This will process all `.webvtt` files under the `c:\subtitles` directory and its subdirectories.

## License

MIT License

