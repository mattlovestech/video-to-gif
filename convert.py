import argparse
import shlex
import subprocess
from pathlib import Path
import imageio_ffmpeg # python version of ffmpeg

VIDEOS = Path("videos") # where the videos are stored
GIFS = Path("gifs") # where the gifs will be saved
VIDEO_EXTS = {".mov", ".mp4", ".avi", ".mkv", ".webm", ".m4v"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert videos/ to gifs/ via ffmpeg")
    parser.add_argument(
        "--ffmpeg-args",
        default="",
        help='Optional extra ffmpeg flags, e.g. --ffmpeg-args "-ss 0 -t 5"',
    )
    args = parser.parse_args()
    extra = shlex.split(args.ffmpeg_args)

    if not VIDEOS.is_dir():
        raise SystemExit(f"Missing {VIDEOS}/ folder. Create it and add video files.")

    GIFS.mkdir(exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    # Only convert known video types. Skips hidden/macOS junk like .DS_Store
    # (fixes .DS_Store issues on Mac where Finder metadata was treated as input).
    videos = [
        p
        for p in VIDEOS.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in VIDEO_EXTS
    ]
    if not videos:
        raise SystemExit(f"No video files found in {VIDEOS}/")

    for src in videos:
        dest = GIFS / f"{src.stem}.gif"
        cmd = [ffmpeg, "-y", *extra, "-i", str(src), str(dest)]
        subprocess.run(cmd, check=True)
        print(dest)


if __name__ == "__main__":
    main()
