# -*- coding: utf-8 -*-
"""Tests."""
import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest import mock

from numerator.main import get_config
from numerator.main import get_target_folder
from numerator.main import run


class BaseFolderTest(TestCase):
    """Base class for tests with folders."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.config = get_config(*['--path', self.tmp_dir.name])
        self.target_folder = get_target_folder(self.config.cwd)
        self.callback = mock.Mock()

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()


class TestRenameNothing(BaseFolderTest):
    """Ensure files without digits are ignored."""

    def setUp(self) -> None:
        super().setUp()
        (Path(self.tmp_dir.name) / 'test.txt').write_bytes(b'')
        (Path(self.tmp_dir.name) / 'other.txt').write_bytes(b'')
        (Path(self.tmp_dir.name) / 'some').write_bytes(b'')
        self.target_folder.parse_contents()

    def test_nothing(self):
        # act
        run(self.target_folder, self.config, self.callback)

        # assert
        self.assertEqual(
            sorted(os.listdir(self.tmp_dir.name)),
            ['other.txt', 'some', 'test.txt'],
        )
        self.callback.assert_not_called()


class TestRenameSimple(BaseFolderTest):
    """Ensure full digit names are treated correctly."""

    def setUp(self) -> None:
        super().setUp()
        (Path(self.tmp_dir.name) / '1.jpg').write_bytes(b'')
        (Path(self.tmp_dir.name) / '02.jpg').write_bytes(b'')
        (Path(self.tmp_dir.name) / '03.jpg').write_bytes(b'')
        (Path(self.tmp_dir.name) / '004.jpg').write_bytes(b'')
        (Path(self.tmp_dir.name) / 'info.txt').write_bytes(b'')
        self.target_folder.parse_contents()

    def test_simple(self):
        # act
        run(self.target_folder, self.config, self.callback)

        # assert
        self.assertEqual(
            sorted(os.listdir(self.tmp_dir.name)),
            ['001.jpg', '002.jpg', '003.jpg', '004.jpg', 'info.txt'],
        )
        self.assertEqual(
            self.callback.call_count,
            3,
        )


class TestRenameComplex(BaseFolderTest):
    """Ensure complex names are treated correctly."""

    def setUp(self) -> None:
        super().setUp()
        (Path(self.tmp_dir.name) / 'my-file-1.jpg').write_bytes(b'')
        (Path(self.tmp_dir.name) / 'my-file-02.jpg').write_bytes(b'')
        (Path(self.tmp_dir.name) / 'my-file-03.jpg').write_bytes(b'')
        (Path(self.tmp_dir.name) / 'my-file-004.jpg').write_bytes(b'')
        (Path(self.tmp_dir.name) / 'info.txt').write_bytes(b'')
        self.target_folder.parse_contents()

    def test_complex(self):
        # act
        run(self.target_folder, self.config, self.callback)

        # assert
        self.assertEqual(
            sorted(os.listdir(self.tmp_dir.name)),
            ['info.txt',
             'my-file-001.jpg',
             'my-file-002.jpg',
             'my-file-003.jpg',
             'my-file-004.jpg'],
        )
        self.assertEqual(
            self.callback.call_count,
            3,
        )


class TestRenameComplexWithReplace(TestRenameComplex):
    """Ensure complex names are treated correctly after replace."""

    def test_complex_with_rename(self):
        # arrange
        self.config = get_config(*['--path',
                                   self.tmp_dir.name,
                                   '--replace', 'my=not-mine',
                                   '--replace', 'file="not file"'])

        # act
        run(self.target_folder, self.config, self.callback)

        # assert
        self.assertEqual(
            sorted(os.listdir(self.tmp_dir.name)),
            ['info.txt',
             'not-mine-not file-001.jpg',
             'not-mine-not file-002.jpg',
             'not-mine-not file-003.jpg',
             'not-mine-not file-004.jpg'],
        )
        self.assertEqual(
            self.callback.call_count,
            4,
        )
