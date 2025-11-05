from helpers.postprocess import parse_vtt_line, read_file, wrap_text_lines
import tempfile
import os


class TestReadFile:
    def test_read_file_merges_lines_without_timestamp(self):
        input_text = (
            '⎡⎡00:00:06.292 --> 00:00:07.459⎦⎦ ⎡⎡Speaker ⎦⎦ "The Challenge."\n'
            '⎡⎡Speaker ⎦⎦ "Survivor."\n'
        )
        expected = [
            '⎡⎡00:00:06.292 --> 00:00:07.459⎦⎦ ⎡⎡Speaker ⎦⎦ "The Challenge." ⎡⎡Speaker ⎦⎦ "Survivor."'
        ]
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
            tmp.write(input_text)
            tmp.flush()
            tmp_path = tmp.name

        try:
            result = read_file(tmp_path)
            assert result == expected
        finally:
            os.remove(tmp_path)

    def test_read_file_splits_multiple_timestamps(self):
        input_text = (
            '⎡⎡00:01:32.125 --> 00:01:36.083⎦⎦ ♪♪♪ ⎡⎡00:01:36.083 --> 00:01:40.334⎦⎦ ♪♪♪ ⎡⎡00:01:40.334 --> 00:01:41.334⎦⎦ Ooh. Ahh. \n'
        )
        expected = [
            '⎡⎡00:01:32.125 --> 00:01:36.083⎦⎦ ♪♪♪',
            '⎡⎡00:01:36.083 --> 00:01:40.334⎦⎦ ♪♪♪',
            '⎡⎡00:01:40.334 --> 00:01:41.334⎦⎦ Ooh. Ahh.'
        ]
        import tempfile
        import os
        with tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8") as tmp:
            tmp.write(input_text)
            tmp.flush()
            tmp_path = tmp.name

        try:
            result = read_file(tmp_path)
            assert result == expected
        finally:
            os.remove(tmp_path)

class TestParseVttLine:
    def test_simple(self):
        line = '⎡⎡00:00:00.167 --> 00:00:01.542⎦⎦ Previously...'
        caption = parse_vtt_line(line)
        assert caption.start == "00:00:00.167"
        assert caption.end == "00:00:01.542"
        assert caption.text == "Previously..."

    def test_named_speaker(self):
        line = '⎡⎡00:00:28.584 --> 00:00:30.083⎦⎦ ⎡⎡Speaker SHAKE:⎦⎦ Ohh!'
        caption = parse_vtt_line(line)
        assert caption.start == "00:00:28.584"
        assert caption.end == "00:00:30.083"
        assert caption.text == "SHAKE: Ohh!"

    def test_multiple_speakers(self):
        line = '⎡⎡00:00:06.292 --> 00:00:07.459⎦⎦ ⎡⎡Speaker ⎦⎦ "The Challenge." ⎡⎡Speaker ⎦⎦ "Survivor."'
        caption = parse_vtt_line(line)
        assert caption.start == "00:00:06.292"
        assert caption.end == "00:00:07.459"
        # Each speaker line should be a separate line
        assert caption.text == '- "The Challenge."\n- "Survivor."'

class TestWrapTextLines:
    def test_wrap_text_lines_basic(self):
        text = "One of you will walk outta here with $200,000 in cash."
        expected = ['One of you will walk outta', 'here with $200,000 in cash.']
        result = wrap_text_lines(text, 30)
        assert result == expected


