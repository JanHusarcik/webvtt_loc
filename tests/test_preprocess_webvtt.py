from unittest.mock import patch, mock_open, MagicMock
from webvtt_loc import preprocess_webvtt
import pprint

class TestPreProcess:
    @patch("preprocess_webvtt.webvtt.read")
    @patch("builtins.open", new_callable=mock_open)
    def test_join_lines(self, mock_file, mock_webvtt_read):
        caption = MagicMock()
        caption.start = "00:00:08.459"
        caption.end = "00:00:12.459"
        caption.text = "She had that level\nof love and care."
        caption.raw_text = "She had that level\nof love and care."
        mock_webvtt_read.return_value = [caption]

        preprocess_webvtt.process_vtt("testfile")

        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        expected = (
            "⎡⎡00:00:08.459 --> 00:00:12.459⎦⎦ She had that level of love and care. \n"
        )

        assert written == expected

    @patch("preprocess_webvtt.webvtt.read")
    @patch("builtins.open", new_callable=mock_open)
    def test_simple_cue(self, mock_file, mock_webvtt_read):
        caption = MagicMock()
        caption.start = "00:00:16.125"
        caption.end = "00:00:20.542"
        caption.text = "I was in shock."
        caption.raw_text = "I was in shock."
        mock_webvtt_read.return_value = [caption]

        preprocess_webvtt.process_vtt("testfile")

        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        expected = "⎡⎡00:00:16.125 --> 00:00:20.542⎦⎦ I was in shock. \n"

        assert written == expected

    @patch("preprocess_webvtt.webvtt.read")
    @patch("builtins.open", new_callable=mock_open)
    def test_join_multiple_cues(self, mock_file, mock_webvtt_read):
        caption1 = MagicMock()
        caption1.start = "00:00:04.667"
        caption1.end = "00:00:06.667"
        caption1.text = "Does Alesia have time to do\nthe crew mess at the moment"
        caption1.raw_text = "Does Alesia have time to do\nthe crew mess at the moment"

        caption2 = MagicMock()
        caption2.start = "00:00:06.667"
        caption2.end = "00:00:08.459"
        caption2.text = "because she's on\nthe hamster wheel."
        caption2.raw_text = "because she's on\nthe hamster wheel."

        mock_webvtt_read.return_value = [caption1, caption2]

        preprocess_webvtt.process_vtt("testfile")

        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        expected = (
            "⎡⎡00:00:04.667 --> 00:00:06.667⎦⎦ Does Alesia have time to do the crew mess at the moment "
            "⎡⎡00:00:06.667 --> 00:00:08.459⎦⎦ because she's on the hamster wheel. \n"
        )

        assert written == expected

    @patch("preprocess_webvtt.webvtt.read")
    @patch("builtins.open", new_callable=mock_open)
    def test_multiple_speakers(self, mock_file, mock_webvtt_read):
        caption = MagicMock()
        caption.start = "00:00:23.042"
        caption.end = "00:00:24.918"
        caption.text = "-A hostel in New York?\n-Yeah."
        caption.raw_text = "-A hostel in New York?\n-Yeah."
        caption.lines = ["-A hostel in New York?", "-Yeah."]
        mock_webvtt_read.return_value = [caption]

        preprocess_webvtt.process_vtt("testfile")

        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        expected = (
            "⎡⎡00:00:23.042 --> 00:00:24.918⎦⎦ "
            "⎡⎡Speaker ⎦⎦ A hostel in New York?\n"
            "⎡⎡Speaker ⎦⎦ Yeah. \n"
        )
        print(written)
        assert written == expected

    @patch("preprocess_webvtt.webvtt.read")
    @patch("builtins.open", new_callable=mock_open)
    def test_multiple_speakers_with_name(self, mock_file, mock_webvtt_read):
        caption = MagicMock()
        caption.start = "00:02:18.125"
        caption.end = "00:02:21.292"
        caption.text = "-Hi, everyone. How are you?\n-TANISHA: Cold."
        caption.raw_text = "-Hi, everyone. How are you?\n-TANISHA: Cold."
        caption.lines = ["-Hi, everyone. How are you?", "-TANISHA: Cold."]
        mock_webvtt_read.return_value = [caption]

        preprocess_webvtt.process_vtt("testfile")

        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        expected = (
            "⎡⎡00:02:18.125 --> 00:02:21.292⎦⎦ "
            "⎡⎡Speaker ⎦⎦ Hi, everyone. How are you?\n"
            "⎡⎡Speaker TANISHA:⎦⎦ Cold. \n"
        )
        print(written)
        assert written == expected


    @patch("preprocess_webvtt.webvtt.read")
    @patch("builtins.open", new_callable=mock_open)
    def test_named_speaker_no_dash(self, mock_file, mock_webvtt_read):
        caption = MagicMock()
        caption.start = "00:00:00.167"
        caption.end = "00:00:03.792"
        caption.text = 'BANANAS: Previously on\n"House of Villains"...'
        caption.raw_text = 'BANANAS: Previously on\n"House of Villains"...'
        # Simulate lines as they would be split by webvtt.models.Caption
        caption.lines = ["BANANAS: Previously on", '"House of Villains"...']
        mock_webvtt_read.return_value = [caption]

        preprocess_webvtt.process_vtt("testfile")

        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        expected = (
            "⎡⎡00:00:00.167 --> 00:00:03.792⎦⎦ "
            "⎡⎡Speaker BANANAS:⎦⎦ Previously on \"House of Villains\"... \n"
        )
        print(written)
        assert written == expected

    @patch("preprocess_webvtt.webvtt.read")
    @patch("builtins.open", new_callable=mock_open)
    def test_multiple_speakers_and_sounds(self, mock_file, mock_webvtt_read):
        # First caption
        caption1 = MagicMock()
        caption1.start = "00:00:55.125"
        caption1.end = "00:00:57.083"
        caption1.text = "-You guys' fashion sucks.\n-[buzzer]"
        caption1.raw_text = "-You guys' fashion sucks.\n-[buzzer]"
        caption1.lines = ["-You guys' fashion sucks.", "-[buzzer]"]

        # Second caption
        caption2 = MagicMock()
        caption2.start = "00:00:57.083"
        caption2.end = "00:00:59.792"
        caption2.text = "-[cackling]\n-Whoo!"
        caption2.raw_text = "-[cackling]\n-Whoo!"
        caption2.lines = ["-[cackling]", "-Whoo!"]

        mock_webvtt_read.return_value = [caption1, caption2]

        preprocess_webvtt.process_vtt("testfile")

        handle = mock_file()
        written = "".join(call.args[0] for call in handle.write.call_args_list)
        expected = (
            "⎡⎡00:00:55.125 --> 00:00:57.083⎦⎦ ⎡⎡Speaker ⎦⎦ You guys' fashion sucks.\n"
            "⎡⎡Speaker ⎦⎦ [buzzer] \n"
            "⎡⎡00:00:57.083 --> 00:00:59.792⎦⎦ ⎡⎡Speaker ⎦⎦ [cackling]\n"
            "⎡⎡Speaker ⎦⎦ Whoo! \n"
        )
        #pprint.pp(written)
        assert written == expected
