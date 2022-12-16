# -*- coding: utf-8 -*-
"""Numerator.

Script that automatically renames files,
so they get equally zero left padded names.
"""
import argparse
import os
import re
import sys
from collections import Counter
from functools import cached_property
from pathlib import Path
from typing import Callable
from typing import Dict
from typing import Iterator
from typing import List
from typing import NamedTuple

DIGITS = re.compile(r'[^0123456789]*([0123456789]+).*')


class Config(NamedTuple):
    """Application configuration."""
    cwd: Path
    replace: Dict[str, str]


def add_padding(
        string: str,
        padding: int,
) -> str:
    """Add padding symbols to the left."""
    match = DIGITS.match(string)

    if match is None:
        return string

    left = match.start(1)
    right = match.end(1)
    left_part = string[:left]
    right_part = string[right:]
    body = match.groups()[0]
    delta = padding - len(body)

    new_filename = left_part + '0' * delta + body + right_part

    return new_filename


def calculate_padding(names: List[str]) -> int:
    """Return max amount of digits on the left side of the name."""
    padding = 0

    for name in names:
        match = DIGITS.match(name)

        if match:
            number = match.groups()[0]
            padding = max(padding, len(number))

    return padding


class File:
    """Helper object that wraps file."""

    def __init__(
            self,
            path: Path,
            filename: str,
    ) -> None:
        """Initialize instance."""
        self.path = path
        self.filename = filename
        self.old_filename = filename
        self.new_filename = filename

    def __repr__(self) -> str:
        """Return textual representation."""
        return f'<File "{self.filename}">'  # pragma: no cover

    @cached_property
    def name(self) -> str:
        """Extract name without extension."""
        return Path(self.filename).stem

    @cached_property
    def ext(self) -> str:
        """Extract extension."""
        suffix = Path(self.filename).suffix
        if suffix.startswith('.'):
            return suffix[1:]
        return suffix

    def looks_like_target(
            self,
            majority: str,
    ) -> bool:
        """Return True if file looks like the type we're interested in."""
        case_folded = self.ext.casefold()
        return all((
            bool(case_folded),
            case_folded == majority.casefold(),
        ))

    def get_new_filename(
            self,
            padding: int,
            replace: Dict[str, str],
    ) -> str:
        """Get new padded filename."""
        new_filename = add_padding(self.old_filename, padding)

        for source, target in replace.items():
            new_filename = new_filename.replace(source, target)

        return new_filename

    def rename_to_pattern(
            self,
            padding: int,
            replace: Dict[str, str],
    ) -> bool:
        """Rename file with name of given pattern, rename True if done."""
        new_filename = self.get_new_filename(padding, replace)

        if new_filename != self.old_filename:
            self.new_filename = new_filename
            (self.path / self.old_filename).rename(
                self.path / self.new_filename)
            return True
        return False


class Folder:
    """Helper object that wraps folder."""

    def __init__(
            self,
            path: Path,
    ) -> None:
        """Initialize instance."""
        self.path = path
        self.files: List[File] = []

    def __repr__(self) -> str:
        """Return textual representation."""
        return f'"{self.path}"'  # pragma: no cover

    def parse_contents(self) -> None:
        """Scan folder contents."""
        self.files = []
        for filename in os.listdir(self.path):
            if (self.path / filename).is_file():
                self.files.append(File(self.path, filename))

    def __iter__(self) -> Iterator[File]:
        """Iterate on files."""
        return iter(self.files)

    @cached_property
    def majority(self) -> str:
        """Return most popular extension in the folder."""
        extensions = [
            file.ext.casefold()
            for file in self.files
            if file.ext.casefold()
        ]
        counter = Counter(extensions)
        return counter.most_common(1)[0][0]

    @cached_property
    def padding(self) -> int:
        """Return amount of zeroes to pad."""
        names = [file.name for file in self.files]
        return calculate_padding(names)


def get_config(*args: str) -> Config:
    """Return application configuration object."""
    parser = argparse.ArgumentParser(
        description='Rename files in folder from '
                    'pattern "1.jpg" to "001.jpg" or similar.'
    )

    parser.add_argument(
        '--path',
        type=str,
        dest='path',
        default=None,
        help='target folder (default: current folder)'
    )

    parser.add_argument(
        '--replace',
        type=str,
        action='append',
        dest='replace',
        default=None,
        help='part of filename that should be replaced, like source=target'
    )

    args = parser.parse_args(args)

    if args.path is not None:
        path = Path(args.path)
    else:
        path = Path(os.getcwd())

    if not path.exists():
        print(f'Directory does not exist: {path.absolute()}')
        sys.exit(1)

    replace: Dict[str, str] = {}
    if args.replace is not None:
        for each in args.replace:
            parts = each.split('=')
            if len(parts) != 2:
                print('Replace argument expects values like: '
                      f'--replace source=target, but got {each!r}')
                sys.exit(1)

            key, value = parts
            key = key.strip("'").strip('"')
            value = value.strip("'").strip('"')
            replace[key] = value

    return Config(
        cwd=path,
        replace=replace,
    )


def get_target_folder(path: Path) -> Folder:
    """Parse actual folder into Folder object and return it."""
    folder = Folder(path)
    folder.parse_contents()
    return folder


def main():
    """Entry point."""
    config = get_config(*sys.argv[1:])
    target_folder = get_target_folder(config.cwd)
    padding = target_folder.padding

    text = f'Renaming files in {target_folder} to padding {padding}'
    if config.replace:
        text += f', using replace {config.replace!r}'

    print(text)

    run(target_folder, config)


def run(
        target_folder: Folder,
        config: Config,
        callback: Callable = print,
) -> None:
    """Apply changes."""
    for file in target_folder:
        if file.looks_like_target(target_folder.majority):
            renamed = file.rename_to_pattern(
                padding=target_folder.padding,
                replace=config.replace,
            )

            if renamed:
                callback(
                    f'\tRenamed {file.old_filename} to {file.new_filename}'
                )


if __name__ == '__main__':
    main()  # pragma: no cover
