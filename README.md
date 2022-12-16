# numerator

Script that automatically renames files, so they get equally zero left padded
names.

## Usage

Imagine you have this folder:

```shell
PS C:\test> ls

    Directory: C:\test

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---          16.12.2022    15:17              0 file-090.jpg
-a---          16.12.2022    15:17              0 file-1.jpg
-a---          16.12.2022    15:17              0 file-100.jpg
-a---          16.12.2022    15:17              0 file-5.jpg
-a---          16.12.2022    15:17              0 file-80.jpg
-a---          16.12.2022    15:17              0 info.txt
```

And you want all files named "file-XXX.jpg" (except for the "info.txt").

Checking possible renames without actual changes:

```shell
pip install numerator
cd C:\test
numerator --dry-run
```

```shell
Renaming 6 files to padding 3
"C:\test"
	1. Planning to rename 'file-1.jpg' to 'file-001.jpg'
	2. Planning to rename 'file-5.jpg' to 'file-005.jpg'
	3. Planning to rename 'file-80.jpg' to 'file-080.jpg'
```

Actual renaming operation:

```shell
cd C:\test
numerator
```

```shell
Renaming 6 files to padding 3
"C:\test"
	1. Renamed 'file-1.jpg' to 'file-001.jpg'
	2. Renamed 'file-5.jpg' to 'file-005.jpg'
	3. Renamed 'file-80.jpg' to 'file-080.jpg'
```

Contents of the folder after execution:

```shell
PS C:\test> ls

    Directory: C:\test

Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
-a---          16.12.2022    15:17              0 file-001.jpg
-a---          16.12.2022    15:17              0 file-005.jpg
-a---          16.12.2022    15:17              0 file-080.jpg
-a---          16.12.2022    15:17              0 file-090.jpg
-a---          16.12.2022    15:17              0 file-100.jpg
-a---          16.12.2022    15:17              0 info.txt
```
