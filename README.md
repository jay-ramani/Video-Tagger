# Video Tagger

## What This Is
A Python script that spawns multiple threads to tag video files with metadata. Currently, only title tagging of .mkv (Matroska format) files is supported.

**Note**: Use a Python 3.6 environment or above to execute the script.

## External Tools Used
Obviously, [Python](https://www.python.org) is used to interpret the script itself. The probing and tagging code uses external tools ('[ffprobe](https://www.ffmpeg.org/)' and '[mkvpropedit](https://mkvtoolnix.download/)'). `ffprobe` is used to probe the currently set metadata (only title for now), and if any different from the title to be set at hand, invoke `mkvpropedit` to set so.

## Where to Download the External Tools From
`ffprobe` is part of the open source ffmpeg package available from https://www.ffmpeg.org, and `mkvpropedit` is part of the open source MKVToolNix package available from https://mkvtoolnix.download.

## Pre-requisites for Use
Ensure you have these external tools installed and define the path appropriately to `mkvpropedit` and `ffprobe` through the following variables under the respective Operating System checks in the function `dict_metadata_tool_platform_get()` in video_tagger.py:

```
path_mkvmerge
path_ffprobe
```

For example:
```python
	if platform.system() == "Windows":
		path_mkvmerge = "C:\\Program Files\\MKVToolNix\\mkvpropedit.exe"
		path_ffprobe  = "C:\\ffmpeg\\bin\\ffprobe.exe"
	else:
		path_mkvmerge = "/usr/bin/mkvpropedit"
		path_ffprobe  = "/usr/bin/ffprobe"
```
**Note**: Windows path separators have to be double escaped using another backslash, as shown in the example above. On Linux, unless these tools have already been added to the PATH environment variable, you would have to update the environment, or manually feed the path.

Also, ensure that files to tag are not read-only. While clearing the attribute can be implemented in the script itself, I will not go about it. Hence, the onus is on the user (you!) to ensure files are write-able (read-only attributes are not set). I will ignore any bug reports relating to the user not setting proper permissions.

If you'd like a tooltip notification on Windows 10 and above, install [win10toast](https://pypi.org/project/win10toast/) with `pip install win10toast`. Tooltips on Linux are supported natively in the script (thanks to `notify-send`).

## How the Currently Set Title is Parsed
My collection of movie files are named in the format below:
```
[year of release] title.mkv
[year of release] title of 3D movie [3D].mkv
```
For example:
```
[1954] Suddenly.mkv
[2009] Avatar [3D].mkv
```
Assuming both the files above don't have titles set, the year and/or a 3D marker (including their square braces) are stripped off to retrieve the true title from the file name itself. The title for [1954] Suddenly.mkv is parsed to "Suddenly", and the title for [2009] Avatar [3D].mkv is parsed to "Avatar".

## How to Batch Process/Use on Single Files
### Batch Processing Recursively/A Selection Through a Simple Right-Click
  On Windows, create a file called "Video Tagger.cmd", or whatever you like but with a .cmd extension, paste the contents as below, and on the Windows Run window, type "shell:sendto" and copy this file in the directory that opens (this is where your items that show up on right-clicking and choosing 'Send To' appear):
```batch
  @echo off
  cls
  set PATH=%PATH%;C:\Python
  :loop_tag
  IF %1=="" GOTO completed
  python "C:\Users\<user login>\Video Tagger\video_tagger.py" --percentage-completion %1
  SHIFT
  GOTO loop_tag
  :completed
```
  Note: In the 3rd line above, ensure you set the path correctly for your Python installation, and in the 6th line, the path to where you download this video tagging file to.

  Once you're done with the above, all you have to do is right-click on any directory (or even a selection of them!) containing Matroska (.mkv) video files, use 'Send To' to send to the command name saved above ('Video Tagger.cmd', as in the example above), and the script will recursively scan through directories and tag your files with the title parsed from every file's name.
  
  I've included this .cmd file as well, so feel free to edit and set parameters according to your installation.

  Since Linux (or any Unix like OS) use varies with a lot of graphical managers, I'm not going to delve into getting verbose here; you can refer your distribution's documentation to figure it out.

### Batch Processing Recursively Through a Command
```
  python "C:\Users\<user login>\Video Tagger\video_tagger.py" --percentage-completion <path to a directory containing Matroska files> <path to another directory...> <you get the picture!>
```
### Tagging Single Files
  If you'd prefer going Hans Solo, use the command below to act on a single file:
```
  python "C:\Users\<user login>\Video Tagger\video_tagger.py" --percentage-completion <path to the Matroska file to tag>
```
## Options
* `--percentage-completion`, or `-p`: This comes handy when tagging a large number of files recursively (either with the right-click 'Send To' option, or through the command line). You might want to skip this option if you'd like the script to execute faster.
* `--help`, or `-h`: Usage help for command line options

## Reporting a Summary
At the end of its execution, the script presents a summary of files probed, tagged, failures (if any) and time taken. Again, this comes in handy when dealing with a large number of files.

## Logging
For a post-mortem, or simply quenching curiosity, a log file is generated with whatever is attempted by the script. This log is generated in the local application data directory (applicable to Windows), under my name (Jay Ramani). For example, this would be `C:\Users\<user login>\AppData\Local\Jay Ramani\video_tagger`.

## TODO (What's Next)
A GUI front-end to make things easy

## Known Issues
*

## Testing and Reporting Bugs
The tagger has been tested on Windows 10, 11 and on Manjaro Linux (XFCE). Would be great if someone can help with testing on other platforms and provide feedback.

To report bugs, use the issue tracker with GitHub.

## End User License Agreement
This software is released under the GNU General Public License version 3.0 (GPL3), and you agree to this license for any use of the software

## Disclaimer
Though not possible, I am not responsible for any corruption of your files. Needless to say, you should always backup before trying anything on your precious data.
