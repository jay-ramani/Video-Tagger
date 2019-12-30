# video-tagger

## What This Does
A Python script to tag video files with metadata. Currently, only title tagging of .mkv (Matroska format) files is supported.

Note: Use a Python 3.6 environment or above to execute the script.

## External Tools Used
Obviously, [Python] (https://www.python.org) is used to interpret the script itself. The probing and tagging code uses external tools (ffprobe and mkvpropedit). 'ffprobe' is used to probe the currently set metadata (only title for now), and if any different from the title to be set at hand, invoke 'mkvpropedit' to set so.

## Where to Download the External Tools From
'ffprobe' is part of the open source ffmpeg package available from https://www.ffmpeg.org, and 'mkvpropedit' is part of the open source MKVToolNix pacakage available from https://mkvtoolnix.download.

## Pre-requisites for Use
Ensure you have these external tools installed and define the path appropriately to 'mkvpropedit' and 'ffprobe' through the following variables under the respective Operating System checks in the function dict_metadata_tool_platform_get() in video_tagger.py:

```
path_mkvmerge
path_ffprobe
```

For example:
```python
	if platform.system() == "Windows":
    path_mkvmerge = "C:\\Program Files\\MKVToolNix\\mkvpropedit.exe"
    path_ffprobe = "C:\\ffmpeg\\bin\\ffprobe.exe"
	else:
		path_mkvmerge = "mkvpropedit"
		path_ffprobe = "ffprobe"
```
Note: Windows path separators have to double escaped using another backslash, as shown in the example above. Unless these tools have already been added to the PATH environment variable, you would have to update the environment, or manually feed the path for use in Linux or one of the Unices.

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
```dos
  @echo off
  cls
  set PATH=%PATH%;C:\Python
  :loop_tag
  IF %1=="" GOTO completed
  python "C:\Users\You\Video Tagger\video_tagger.py" --percentage-completion %1
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
  python "C:\Users\You\Video Tagger\video_tagger.py" --percentage-completion <path to a directory containing Matroska files> <path to another directory...> <you get the picture!>
```
### Tagging Single Files
  If you'd prefer going Hans Solo, use the command below to act on a single file:
```
  python "C:\Users\You\Video Tagger\video_tagger.py" --percentage-completion <path to the Matroska file to tag>
```
## Options
The only option supported currently is to report the percentage of completion: --percentage-completion, or simply: -p. This comes handy when tagging a large number of files recursively (either with the right-click 'Send To' option, or through the command line).

You might want to skip this option if you'd like the script to execute a bit faster.

## Reporting a Summary
At the end of its execution, the script presents a summary of files probed, tagged, failures (if any) and time taken. Again, this comes in handy when dealing with a large number of files.

## Testing and Reporting Bugs
The tagger has been tested on Windows 10, and is *untested* on Linux and other Unices. Would be great if someone can help with testing on these platforms and provide feedback.

To report bugs, use the issue tracker with GitHub.

## End User License Agreement
This software is released under the GNU General Public License version 3.0 (GPL3), and you agree to this license for any use of the software

## Disclaimer
Though not possible, I am not responsible for any corruption of your files. Needless to say, you should always backup before trying anything on your precious data.
