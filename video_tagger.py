# -------------------------------------------------------------------------------
# Name        : Video Resolution
# Purpose     : Set metadata in video using format specific tools
#             : Note: Requires a path defined for each tool
# Author      : Jayendran Jayamkondam Ramani
# Created     : 1:30 PM + 5:30 IST 19 March 2017
# Copyright   : (c) Jayendran Jayamkondam Ramani
# Licence     : GPL v3
# Dependencies: Requires the following packages to be installed as pre-requisites
#                   - win10toast (pip install win10toast; for Windows 10 toast notifications)
# -------------------------------------------------------------------------------

import logging
import os
import platform
import subprocess
import sys
import time
import math
import argparse

from contextlib import suppress
from win10toast import ToastNotifier

INDEX_TOOL_PATH = 0
INDEX_TOOL_OPTIONS = 1


# Show tool tip/notification/toast message
def show_toast(tooltip_title, tooltip_message):
	# Handle tool tip notification (Linux)/balloon tip (Windows; only OS v10 supported for now)
	tooltip_message = os.path.basename(__file__) + ": " + tooltip_message

	if platform.system() == "Linux":
		os.system("notify-send \"" + tooltip_title + "\" \"" + tooltip_message + "\"")
	else:
		toaster = ToastNotifier()
		toaster.show_toast(tooltip_title, tooltip_message, icon_path = None, duration = 5)


# Use a dictionary to map a metadata tool (key) to its file type (value) and the tool's options
def dict_metadata_tool_platform_get(extension, title_set, path_file):
	if platform.system() == "Windows":
		path_mkvmerge = "C:\\Program Files\\MKVToolNix\\mkvpropedit.exe"
		path_ffprobe = "C:\\ffmpeg\\bin\\ffprobe.exe"
	else:
		path_mkvmerge = "mkvpropedit"
		path_ffprobe = "ffprobe"

	options_probe_ffprobe = (
		"-v", "error", "-select_streams", "v:0", "-show_entries", "format_tags=title", "-print_format",
		"default=noprint_wrappers=1:nokey=1", "-i", path_file)

	options_metadata_mkvmerge = ("--edit", "info", "--set", "title=" + title_set.decode("utf-8"), path_file)

	dict_path_tool_metadata = {
		path_mkvmerge: (("mkv"), options_metadata_mkvmerge)
	}

	dict_path_tool_probe = {
		path_ffprobe: (("mkv", "avi", "divx", "mp4", "m4v", "mpg", "mpeg"), options_probe_ffprobe)
	}

	tool_metadata = options_tool_metadata = None
	metadata = (tool_metadata, options_tool_metadata)

	# Look up the metadata binary's path and its options for the format we received
	for tool_metadata, formats_and_options in dict_path_tool_metadata.items():
		if extension in formats_and_options[0]:
			metadata = (tool_metadata, formats_and_options[1])

			break

	tool_probe = options_tool_probe = None
	probe = (tool_probe, options_tool_probe)

	# Look up the probe binary's path and its options for the format we received
	for tool_probe, formats_and_options in dict_path_tool_probe.items():
		if extension in formats_and_options[0]:
			probe = (tool_probe, formats_and_options[1])

			break

	return metadata, probe


# Return a tuple of formats supported by the probe tool (ffprobe)
def probe_formats_supported_get():
	return ("mkv", "avi", "divx", "mp4", "m4v", "mpg", "mpeg")


# We support only Windows and Unix like OSes
def is_supported_platform():
	return platform.system() == "Windows" or platform.system() == "Linux"


def logging_initialize(root):
	logging.basicConfig(filename = root + " - " + time.strftime("%Y%m%d%I%M%S%z") + '.log', level = logging.INFO,
	                    format = "%(message)s")
	logging.info("Log beginning at " + time.strftime("%d %b %Y (%a) %I:%M:%S %p %Z (GMT%z)") + " with PID: " + str(
		os.getpid()) + ", started with arguments " + str(sys.argv) + "\n")


def parse_file_name_from_path(root):
	# Grab only the file name without the preceding path. The extension has already
	# been stripped off by the caller.
	title = os.path.basename(root)

	# Extract title from the year used in the naming convention "[yyyy] Title of the movie"
	# If the movie is 3D, the title would contain the string at the name's tail, viz., "[yyyy] Title of the movie [3D]"

	# Check if the file contains [3D] in its name
	if title.partition("[3D]")[1]:
		# We stepped on a 3D file, grab content before the "[3D]" part
		title = title.partition("[3D]")[0]

	# If we find year information in the file name, tokenize the year and video title
	release_year = title.partition("[")[2]

	if release_year:
		release_year = release_year.partition("]")[0]

		# The file name adheres to the convention used. Grab the name alone.
		title = title.partition("]")[2]

		# Strip the white space after the year's closing brace [yyyy]_Title
		#                                                            ^
		title = title.strip()

	return title, release_year


# Print a spacer to differentiate between outputs
def print_and_log_spacer():
	print("----- ----- ----- ----- -----")
	logging.info("----- ----- ----- ----- -----")


# Print completion status at every checkpoint defined by CHECKPOINT_FILES_QUERIED
def percentage_completion_print(count_processed, count_total):
	# Default CHECKPOINT_FILES_QUERIED to 1% of the files to be processed
	CHECKPOINT_FILES_QUERIED = round(count_total * (1 / 100))

	# If count_total is too low, set CHECKPOINT_FILES_QUERIED accordingly for
	# printing progress after every file. This is to prevent a divide-by-zero
	# error during printing progress down below if CHECKPOINT_FILES_QUERIED is
	# zero.
	if not CHECKPOINT_FILES_QUERIED:
		CHECKPOINT_FILES_QUERIED = 1

	# For every checkpoint defined in CHECKPOINT_FILES_QUERIED, print percentage completion
	if not (count_processed % CHECKPOINT_FILES_QUERIED):
		if count_processed < count_total:
			percent_complete = str(
				math.floor((count_processed / count_total) * 100))

			print("\n-------------------------------------------")
			logging.info("-------------------------------------------")

			print(percent_complete + "% (" + str(count_processed) + "/" + str(
				count_total) + ") of files in queue processed")
			logging.info(percent_complete + "% (" + str(count_processed) + "/" + str(
				count_total) + ") of files in queue processed")

			print("-------------------------------------------\n\n")
			logging.info("-------------------------------------------\n")
		else:
			print("\nAll files in queue processed\n")
			logging.info("\nAll files in queue processed\n")


# Retrieve currently set title and return in UTF-8 encoding
def get_current_metadata(probe, path_file, list_failed_files_probe):
	title_current = ""

	# Retrieve the file's current title from it's metadata, if at all set
	# Check if the probe tool exists in the path defined
	if os.path.isfile(probe[INDEX_TOOL_PATH]):
		# Keep track of the number of files thrown for probing to present a total statistic at exit
		get_current_metadata.total_count_files += 1

		# Track probe start time in nano-seconds
		time_start = time.monotonic_ns()

		try:
			output_probe = subprocess.run((probe[INDEX_TOOL_PATH], *probe[INDEX_TOOL_OPTIONS]),
			                              universal_newlines = True, stdout = subprocess.PIPE, check = True).stdout
		except subprocess.CalledProcessError as error_metadata_probe:
			if error_metadata_probe.stderr:
				print(error_metadata_probe.stderr)
				logging.info(error_metadata_probe.stderr)
			if error_metadata_probe.output:
				print(error_metadata_probe.output)
				logging.error(error_metadata_probe.output)

			print("Command that resulted in the exception: " + str(error_metadata_probe.cmd) + "\n")
			logging.error("Command that resulted in the exception: " + str(error_metadata_probe.cmd) + "\n")

			print("Error probing metadata from \'" + path_file + "\'")
			print("Error", sys.exc_info())
			logging.error("Error probing metadata from \'" + path_file + "\'" + str(sys.exc_info()))

			show_toast("Error", "Failed to probe the title for one or more files. Check the log.")

			# Append the failed file to a list that will be reported at exit
			list_failed_files_probe.append(path_file)
		else:
			# Track probe end time in nano-seconds
			time_end = time.monotonic_ns()

			title_current = (output_probe.strip()).encode("utf-8")

			# Keep track of the number of files probed to present a total statistic at exit
			get_current_metadata.total_count_probe += 1
			# Save the total time taken to probe files thrown at us, to report a statistic at exit
			get_current_metadata.total_time_probe += time_end - time_start
	else:
		print("No probe tool found at \'" + probe[INDEX_TOOL_PATH] + "\' to read currently set title\n")
		logging.error("No probe tool found at \'" + probe[INDEX_TOOL_PATH] + "\' to read currently set title\n")

	return title_current


get_current_metadata.total_count_files = 0
get_current_metadata.total_count_probe = 0
get_current_metadata.total_time_probe = 0


# Writes metadata parsed from the file name into the video file's tag
#
# Fields currently written:
# - Title
def set_metadata(path_file, list_failed_files_probe, list_failed_files_metadata_set, percentage_gather = False):
	root, extension = os.path.splitext(path_file)

	# Strip the '.' from the extension passed in, and convert  to lower case.
	# This is to ensure we don't skip files with extensions that Windows sets
	# to upper case. This is often the case with server downloaded files or
	# torrents.
	extension = (extension.partition(os.path.extsep)[2]).lower()

	title_set, release_year = parse_file_name_from_path(root)

	# Encode the title to UTF-8 for non-ASCII characters. While it may not get
	# printed properly in the logs, mkvpropedit accepts UTF-8 characters as
	# input, by default. Unless, the user has modified OS behaviour, this is
	# sure to get through.
	title_set = title_set.encode("utf-8")

	# Only process video files
	metadata, probe = dict_metadata_tool_platform_get(extension, title_set, path_file)

	# Proceed only if a metadata tool has been defined
	if all(metadata) and all(probe):
		# We got a valid tool to write metadata

		if percentage_gather:
			# We're only here to gather headcount
			set_metadata.total_count_percentage += 1

			return

		# Get the current title
		title_current = get_current_metadata(probe, path_file, list_failed_files_probe)

		if title_current == title_set:
			# Nothing to do, if the current title is the same as the title to be set
			print("The current title is already set to \'" + title_set.decode(
				"utf-8") + "\' in \'" + path_file + "\'. Will skip processing...\n")
			logging.info("The current title is already set to \'" + title_set.decode(
				"utf-8") + "\' in \'" + path_file + "\'. Will skip processing...\n")
		else:
			# The titles are different; do the needful
			if title_current:
				# If the string is already Unicode, suppress the exception
				with suppress(Exception):
					title_current = title_current.encode("utf-8")

				print("The currently set title is \'" + title_current.decode("utf-8") + "\'\n")
				logging.info("The currently set title is \'" + title_current.decode("utf-8") + "\'\n")
			else:
				print("No title currently set in \'" + path_file + "\'\n")
				logging.info("No title currently set in \'" + path_file + "\'\n")

			# Check if the metadata tool exists in the path defined
			if os.path.isfile(metadata[INDEX_TOOL_PATH]):
				set_metadata.total_count_files += 1

				# TODO: Build a tag with the year of release to slap the mkv container with
				# Writing the year with mkvpropedit is not supported by the MKV format developers!
				# It has to be tagged separately with a tag. How lame can it be?

				time_start = time.monotonic_ns()

				try:
					output = subprocess.run((metadata[INDEX_TOOL_PATH], *metadata[INDEX_TOOL_OPTIONS]), check = True,
					                        universal_newlines = True, stdout = subprocess.PIPE).stdout
				except subprocess.CalledProcessError as error_metadata_set:
					if error_metadata_set.stderr:
						print(error_metadata_set.stderr)
						logging.info(error_metadata_set.stderr)
					if error_metadata_set.output:
						print(error_metadata_set.output)
						logging.error(error_metadata_set.output)

					print("Command that resulted in the exception: " + str(error_metadata_set.cmd) + "\n")
					logging.info("Command that resulted in the exception: " + str(error_metadata_set.cmd) + "\n")

					print("Error setting metadata in \'" + path_file + "\'")
					print("Error", sys.exc_info())
					logging.error("Error setting metadata in \'" + path_file + "\'" + str(sys.exc_info()))

					# Append the failed file to a list that will be reported at exit
					list_failed_files_metadata_set.append(path_file)

					show_toast("Error", "Failed to tag \'" + path_file + "\'. Check the log for details.")
				else:
					time_end = time.monotonic_ns()

					# Keep track of the number of files tagged to present a total statistic at exit
					set_metadata.total_count_set += 1
					# Keep track of the total time taken to tag files thrown at us to report a statistic at exit
					set_metadata.total_time_set += time_end - time_start

					if output:
						print(output)
						logging.info(output)

					print("Tagged file# " + "{:>4}".format(
						set_metadata.total_count_set) + ": \'" + path_file + "\' with title (" + title_set.decode(
						"utf-8") + ")...\n")
					logging.info("Tagged file# " + "{:>4}".format(
						set_metadata.total_count_set) + ": \'" + path_file + "\' with title (" + title_set.decode(
						"utf-8") + ")...\n")
			else:
				print("No metadata tool found at \'" + metadata[INDEX_TOOL_PATH] + "\'\n")
				logging.error("No metadata tool found at \'" + metadata[INDEX_TOOL_PATH] + "\'\n")

		# This would have a (positive) non-zero value only if the percentage was asked to be reported
		if set_metadata.total_count_percentage:
			# Setting metadata involves probing. The probed count reflects the actual number of files processed.
			percentage_completion_print(get_current_metadata.total_count_probe, set_metadata.total_count_percentage)


set_metadata.total_count_set = 0
set_metadata.total_count_percentage = 0
set_metadata.total_count_files = 0
set_metadata.total_time_set = 0


# Convert the time in nanoseconds passed to hours, minutes and seconds as a string
def total_time_in_hms_get(total_time_ns):
	seconds_raw = total_time_ns / 1000000000
	seconds = round(seconds_raw)
	hours = minutes = 0

	if seconds >= 60:
		minutes = round(seconds / 60)
		seconds = seconds % 60

	if minutes >= 60:
		hours = round(minutes / 60)
		minutes = minutes % 60

	# If the quantum is less than a second, we need show a better resolution. A fractional report matters only when
	# it's less than 1.
	if (not (hours and minutes)) and (seconds_raw < 1 and seconds_raw > 0):
		# Round off to two decimals
		seconds = round(seconds_raw, 2)
	elif (not (hours and minutes)) and (seconds_raw < 60 and seconds_raw > 1):
		# Round off to the nearest integer, if the quantum is less than a minute. A fractional report doesn't matter
		# when it's more than 1.
		seconds = round(seconds_raw)

	return (str(hours) + " hour(s) " if hours else "") + (str(minutes) + " minutes " if minutes else "") + (str(
		seconds) + " seconds")


def statistic_print(list_failed_files_probe, list_failed_files_metadata_set):
	if len(list_failed_files_probe):
		print_and_log_spacer()

		print("\aHere's the list of the " + str(len(list_failed_files_probe)) + " files for which probing failed:\n")
		logging.info(
			"Here's the list of the " + str(len(list_failed_files_probe)) + " files for which probing failed:\n")

		for failed_file in list_failed_files_probe:
			print(failed_file)
			logging.info(failed_file)

	if len(list_failed_files_metadata_set):
		print_and_log_spacer()

		print("\aHere's the list of the " + str(
			len(list_failed_files_metadata_set)) + " files for which setting metadata failed:\n")
		logging.info("Here's the list of the " + str(
			len(list_failed_files_metadata_set)) + " files for which setting metadata failed:\n")

		for failed_file in list_failed_files_metadata_set:
			print(failed_file)
			logging.info(failed_file)

	print("\nProbed a total of " + str(get_current_metadata.total_count_probe) + "/" + str(
		get_current_metadata.total_count_files) + " in " + total_time_in_hms_get(
		get_current_metadata.total_time_probe) + " and tagged a total of " + str(
		set_metadata.total_count_set) + "/" + str(
		set_metadata.total_count_files) + " files in " + total_time_in_hms_get(set_metadata.total_time_set))
	logging.info("\nProbed a total of " + str(get_current_metadata.total_count_probe) + "/" + str(
		get_current_metadata.total_count_files) + " in " + total_time_in_hms_get(
		get_current_metadata.total_time_probe) + " and tagged a total of " + str(
		set_metadata.total_count_set) + "/" + str(
		set_metadata.total_count_files) + " files in " + total_time_in_hms_get(set_metadata.total_time_set))


# For reading tags with UTF-8 encoding, we need a UTF-8 enabled console (or command prompt, in Windows parlance).
# This is applicable for writing tags as well. So warn the user to have the pre-requisite ready.
def sound_utf8_warning():
	print(
		"** Important: Non-ASCII characters in path and the video title require a UTF-8 enabled console/command prompt "
		"for reading and writing tags properly **\n\n")
	logging.info(
		"** Important: Non-ASCII characters in path and the video title require a UTF-8 enabled console/command prompt "
		"for reading and writing tags properly **\n\n")


# Parse command line arguments and return option and/or values of action
def cmd_line_parse(opt_percentage):
	parser = argparse.ArgumentParser(
		description = "Tags supported video files with the title formed from the file's name", add_help = True)
	parser.add_argument("-p", opt_percentage, required = False, action = "store_true",
	                    default = None, dest = "percentage",
	                    help = "Show the percentage of files completed (not the actual data processed; just the files")

	result_parse, files_to_process = parser.parse_known_args()

	return result_parse.percentage, files_to_process


def main(argv):
	exit_code = 0

	if is_supported_platform():
		root, _ = os.path.splitext(sys.argv[0])

		opt_percentage = "--percentage-completion"

		percentage, files_to_process = cmd_line_parse(opt_percentage)

		if files_to_process:
			logging_initialize(root)
			sound_utf8_warning()

			# Change to the working directory of this Python script. Else, any dependencies will not be found.
			os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

			print("Changing working directory to \'" + os.path.dirname(os.path.abspath(sys.argv[0])) + "\'...\n")
			logging.info("Changing working directory to \'" + os.path.dirname(os.path.abspath(sys.argv[0])) + "\'...\n")

			# A list containing the files for which we failed to set metadata.
			# Used to provide a summary of the erroneous files at the end of all.
			list_failed_files_probe = []
			list_failed_files_metadata_set = []

			if percentage:
				# Gather a headcount for reporting percentage completion
				for path in files_to_process:
					if os.path.isdir(path):
						# If it's a directory, walk through for files below
						for path_dir, _, file_names in os.walk(path):
							for file_name in file_names:
								path_file = os.path.join(path_dir, file_name)
								set_metadata(path_file, list_failed_files_probe, list_failed_files_metadata_set,
								             percentage)
					else:
						# We got a file, do the needful
						set_metadata(path, list_failed_files_probe, list_failed_files_metadata_set, percentage)

				# We've already gathered the headcount, so flag accordingly
				percentage = False

			# The actual loop for probing and tagging
			for path in files_to_process:
				if os.path.isdir(path):
					# If it's a directory, walk through for files below
					for path_dir, _, file_names in os.walk(path):
						for file_name in file_names:
							path_file = os.path.join(path_dir, file_name)
							set_metadata(path_file, list_failed_files_probe, list_failed_files_metadata_set, percentage)
				else:
					# We got a file, do the needful
					set_metadata(path, list_failed_files_probe, list_failed_files_metadata_set, percentage)

			statistic_print(list_failed_files_probe, list_failed_files_metadata_set)
		# Slows down the script exit, so disabled for now
		# show_completion_toast(argv[0])
		else:
			print("\aThis program requires at least one argument")
			logging.error("This program requires at least one argument")

			exit_code = 1
	else:
		print("\aUnsupported OS")
		logging.error("Unsupported OS")

		exit_code = 1

	return exit_code


if __name__ == '__main__':
	main(sys.argv)
