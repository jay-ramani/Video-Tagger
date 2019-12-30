@echo off
cls
set PATH=%PATH%;C:\Python
:loop_tag
IF %1=="" GOTO completed
python "C:\Users\You\Video Tagger\video_tagger.py" --percentage-completion %1
SHIFT
GOTO loop_tag
:completed
