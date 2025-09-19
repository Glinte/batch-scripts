#!/usr/bin/python3
#
# Script by EmmetJoe009: https://pastebin.com/t3Bh2kNU
# /// script
# requires-python = ">=3.9"
# ///

import sys
import subprocess
import os
import argparse
import time

startTime: float = time.time()

parser: argparse.ArgumentParser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='File to Crush', required=True)
parser.add_argument('-o', '--output', help='Output File', required=False)
parser.add_argument("-s", "--size", help="Target Size in MB", type=int, default=8)
parser.add_argument("-t", "--tolerance", help="Tolerance", type=int, default=10)
args: argparse.Namespace = parser.parse_args()


def get_duration(fileInput: str) -> float:
    return float(
        subprocess.check_output([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            fileInput
        ])[:-1]
    )


def transcode(fileInput: str, fileOutput: str, bitrate: int) -> None:
    command: list[str] = [
        'ffmpeg',
        '-y',
        '-hide_banner',
        '-loglevel', 'error',
        '-i', fileInput,
        '-b', str(bitrate) + '',
        '-cpu-used', str(os.cpu_count()),
        '-c:a',
        'copy',
        fileOutput
    ]

    proc: subprocess.CompletedProcess[str] = subprocess.run(
        command,
        capture_output=True,
        # avoid having to explicitly encode
        text=True
    )


tolerance: int = args.tolerance
fileInput: str = args.file
if args.output:
    fileOutput: str = args.output
else:
    fileOutput: str = fileInput[:fileInput.rindex('.')] + '.crushed' + fileInput[fileInput.rindex('.'):]
targetSizeKilobytes: int = args.size * 1024
targetSizeBytes: int = targetSizeKilobytes * 1024
durationSeconds: float = get_duration(fileInput)
bitrate: int = round(targetSizeBytes / durationSeconds)
beforeSizeBytes: int = os.stat(fileInput).st_size

print(f"Crushing {fileInput} to {targetSizeKilobytes} KB with tolerance {tolerance}%")

factor: float = 0
attempt: int = 0
while (factor > 1.0 + (tolerance / 100)) or (factor < 1):
    attempt = attempt + 1
    bitrate = round(bitrate * (factor or 1))
    print(f"Attempt {attempt}: Transcoding {fileInput} at bitrate {bitrate}")

    transcode(fileInput, fileOutput, bitrate)
    afterSizeBytes: int = os.stat(fileOutput).st_size
    percentOfTarget: float = (100 / targetSizeBytes) * afterSizeBytes
    factor = 100 / percentOfTarget
    print(
        f"Attempt {attempt}: Original size: {beforeSizeBytes / 1024 / 1024:.2f} MB, "
        f"New size: {afterSizeBytes / 1024 / 1024:.2f} MB, "
        f"Percentage of target: {percentOfTarget:.0f}% and bitrate {bitrate}"
    )

print(f"Completed in {attempt} attempts over {round(time.time() - startTime, 2)} seconds")
print(f" > Exported as {fileOutput}")