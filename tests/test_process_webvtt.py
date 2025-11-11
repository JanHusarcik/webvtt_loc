import pytest
from unittest.mock import patch, MagicMock
from process_webvtt import main
import webvtt
import os
import re
import tempfile
import shutil
from helpers import preprocess, postprocess
from time import sleep
import pprint


class TestMain:
    @patch("process_webvtt.helpers.logging.create_log")
    @patch("process_webvtt.helpers.preprocess.process_vtt")
    @patch("process_webvtt.glob.glob")
    @patch("process_webvtt.os.path.isdir")
    @patch("process_webvtt.os.path.isfile")
    @patch("process_webvtt.argparse.ArgumentParser.parse_args")
    def test_main_single_file_prepare(
        self,
        mock_parse_args,
        mock_isfile,
        mock_isdir,
        mock_glob,
        mock_preprocess_vtt,
        mock_create_log,
    ):
        mock_logger = MagicMock()
        mock_create_log.return_value = mock_logger
        # Simulate single file, prepare action
        mock_args = MagicMock(path="file.webvtt", action="prepare")
        mock_parse_args.return_value = mock_args
        mock_isfile.return_value = True
        mock_isdir.return_value = False
        main()
        mock_preprocess_vtt.assert_called_once_with("file.webvtt", mock_logger)
        mock_logger.info.assert_any_call(
            "Starting", action="prepare", path="file.webvtt"
        )

    @patch("process_webvtt.helpers.logging.create_log")
    @patch("process_webvtt.helpers.postprocess.process_vtt")
    @patch("process_webvtt.glob.glob")
    @patch("process_webvtt.os.path.isdir")
    @patch("process_webvtt.os.path.isfile")
    @patch("process_webvtt.argparse.ArgumentParser.parse_args")
    def test_main_single_file_finalize(
        self,
        mock_parse_args,
        mock_isfile,
        mock_isdir,
        mock_glob,
        mock_postprocess_vtt,
        mock_create_log,
    ):
        mock_logger = MagicMock()
        mock_create_log.return_value = mock_logger
        # Simulate single file, finalize action
        mock_args = MagicMock(path="file.webvtt", action="finalize")
        mock_parse_args.return_value = mock_args
        mock_isfile.return_value = True
        mock_isdir.return_value = False
        main()
        mock_postprocess_vtt.assert_called_once_with("file.webvtt", mock_logger)
        mock_logger.info.assert_any_call(
            "Starting", action="finalize", path="file.webvtt"
        )

    @patch("process_webvtt.helpers.logging.create_log")
    @patch("process_webvtt.helpers.preprocess.process_vtt")
    @patch("process_webvtt.glob.glob")
    @patch("process_webvtt.os.path.isdir")
    @patch("process_webvtt.os.path.isfile")
    @patch("process_webvtt.argparse.ArgumentParser.parse_args")
    def test_main_directory_prepare(
        self,
        mock_parse_args,
        mock_isfile,
        mock_isdir,
        mock_glob,
        mock_preprocess_vtt,
        mock_create_log,
    ):
        mock_logger = MagicMock()
        mock_create_log.return_value = mock_logger
        # Simulate directory with files, prepare action
        mock_args = MagicMock(path="dir", action="prepare")
        mock_parse_args.return_value = mock_args
        mock_isfile.return_value = False
        mock_isdir.return_value = True
        mock_glob.return_value = ["dir/a.webvtt", "dir/b.webvtt"]
        main()
        mock_preprocess_vtt.assert_any_call("dir/a.webvtt", mock_logger)
        mock_preprocess_vtt.assert_any_call("dir/b.webvtt", mock_logger)
        assert mock_preprocess_vtt.call_count == 2
        mock_logger.info.assert_any_call("Starting", action="prepare", path="dir")

    @patch("process_webvtt.helpers.logging.create_log")
    @patch("process_webvtt.helpers.postprocess.process_vtt")
    @patch("process_webvtt.glob.glob")
    @patch("process_webvtt.os.path.isdir")
    @patch("process_webvtt.os.path.isfile")
    @patch("process_webvtt.argparse.ArgumentParser.parse_args")
    def test_main_directory_finalize(
        self,
        mock_parse_args,
        mock_isfile,
        mock_isdir,
        mock_glob,
        mock_postprocess_vtt,
        mock_create_log,
    ):
        mock_logger = MagicMock()
        mock_create_log.return_value = mock_logger
        # Simulate directory with files, finalize action
        mock_args = MagicMock(path="dir", action="finalize")
        mock_parse_args.return_value = mock_args
        mock_isfile.return_value = False
        mock_isdir.return_value = True
        mock_glob.return_value = ["dir/a.webvtt", "dir/b.webvtt"]
        main()
        mock_postprocess_vtt.assert_any_call("dir/a.webvtt", mock_logger)
        mock_postprocess_vtt.assert_any_call("dir/b.webvtt", mock_logger)
        assert mock_postprocess_vtt.call_count == 2
        mock_logger.info.assert_any_call("Starting", action="finalize", path="dir")

    @patch("process_webvtt.helpers.logging.create_log")
    @patch("process_webvtt.argparse.ArgumentParser.parse_args")
    @patch("process_webvtt.os.path.isfile")
    @patch("process_webvtt.os.path.isdir")
    def test_main_invalid_path(
        self, mock_isdir, mock_isfile, mock_parse_args, mock_create_log
    ):
        mock_logger = MagicMock()
        mock_create_log.return_value = mock_logger
        mock_args = MagicMock(path="invalid", action="prepare")
        mock_parse_args.return_value = mock_args
        mock_isfile.return_value = False
        mock_isdir.return_value = False

        with pytest.raises(Exception) as excinfo:
            main()
        assert "Path invalid is not valid." in str(excinfo.value)


class TestRoundtrip:
    def normalize(self, text:str) ->str:
        # Normalize text for comparison (strip, unify whitespace)
        normalized = re.sub(r"(?m)^\s*-(?!-)\s*", "- ", text)
        normalized=" ".join(normalized.strip().split())
        return normalized

    def equality(self, cap1:webvtt.Caption, cap2:webvtt.Caption)->bool:
        # Compare start, end, and normalized text
        return (
            cap1.start == cap2.start
            and cap1.end == cap2.end
            and self.normalize(cap1.text) == self.normalize(cap2.text)
        )

    def test_roundtrip(self):
        # Setup temp directory for prepared/final files
        with tempfile.TemporaryDirectory() as tmpdir:
            orig_file = os.path.join(os.path.dirname(__file__), "sample1.webvtt")
            # Copy original to temp to avoid modifying source
            test_file = os.path.join(tmpdir, "sample1.webvtt")
            shutil.copyfile(orig_file, test_file)

            # Run preprocess to create prepared file
            logger = MagicMock()
            preprocess.process_vtt(test_file, logger)
            prepared_file = os.path.join(tmpdir, "prepared", "sample1.webvtt")
            # Run postprocess to create finalized file
            postprocess.process_vtt(prepared_file, logger)
            finalized_file = os.path.join(tmpdir, "prepared", "final", "sample1.webvtt.vtt")
            if not os.path.exists(finalized_file):
                # fallback for postprocess output location
                finalized_file = os.path.join(tmpdir, "final", "sample1.webvtt")
            # Parse original and finalized files
            orig_vtt = webvtt.read(test_file)
            final_vtt = webvtt.read(finalized_file)

            # Compare number of captions
            assert len(orig_vtt.captions) == len(final_vtt.captions), (
                "Caption count mismatch"
            )

            # Compare each caption
            for orig_cap, final_cap in zip(orig_vtt.captions, final_vtt.captions):
                assert self.equality(orig_cap, final_cap), (
                    f"Mismatch:\n"
                    f"Original (not normalized):\n{orig_cap.start}-{orig_cap.end}\n{orig_cap.text}\n"
                    f"Final:\n{final_cap.start}-{final_cap.end}\n{final_cap.text}"
                )
