import pytest
from unittest.mock import patch, MagicMock
from process_webvtt import main


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
