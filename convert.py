import argparse
import re
import subprocess
from pathlib import Path
import imageio_ffmpeg  # python version of ffmpeg

VIDEOS = Path("videos")
GIFS = Path("gifs")
VIDEO_EXTS = {".mov", ".mp4", ".avi", ".mkv", ".webm", ".m4v"}


def mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def probe(ffmpeg: str, path: Path) -> tuple[str, float | None, float | None]:
    """Return scale, fps, duration from ffmpeg."""
    text = subprocess.run([ffmpeg, "-i", str(path)], capture_output=True, text=True).stderr
    scale = re.search(r"(\d{2,5})x(\d{2,5})", text)
    fps = re.search(r"([\d.]+)\s*fps", text)
    dur = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", text)
    duration = None
    if dur:
        h, m, s = dur.groups()
        duration = int(h) * 3600 + int(m) * 60 + float(s)
    return (
        f"{scale.group(1)}x{scale.group(2)}" if scale else "?",
        float(fps.group(1)) if fps else None,
        duration,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert videos/ to gifs. Extra args are passed through to ffmpeg.",
        epilog=(
            "Examples:\n"
            "  python convert.py\n"
            "  python convert.py -vf fps=15,scale=640:-1\n"
            "  python convert.py -ss 0 -t 5 -- -vf fps=12\n"
            "\n"
            "Args before -- are input options (before -i). "
            "Args after -- (or all args if no --) are output options (after -i)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _, extra = parser.parse_known_args()
    if "--" in extra:
        split = extra.index("--")
        in_opts, out_opts = extra[:split], extra[split + 1 :]
    else:
        # Default: treat as output options (after -i), same as typical ffmpeg filters
        in_opts, out_opts = [], extra

    if not VIDEOS.is_dir():
        raise SystemExit(f"Missing {VIDEOS}/ folder. Create it and add video files.")

    GIFS.mkdir(exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

    # Skip hidden/macOS junk like .DS_Store
    videos = [
        p
        for p in VIDEOS.iterdir()
        if p.is_file() and not p.name.startswith(".") and p.suffix.lower() in VIDEO_EXTS
    ]
    if not videos:
        raise SystemExit(f"No video files found in {VIDEOS}/")

    rows = []
    for i, src in enumerate(videos):
        dest = GIFS / f"{src.stem}.gif"
        # Same order as ffmpeg: [input opts] -i input [output opts] output
        subprocess.run(
            [ffmpeg, "-y", *in_opts, "-i", str(src), *out_opts, str(dest)],
            check=True,
        )

        in_mb, out_mb = mb(src), mb(dest)
        in_scale, in_fps, in_dur = probe(ffmpeg, src)
        out_scale, out_fps, out_dur = probe(ffmpeg, dest)
        in_speed = 1.0
        out_speed = (in_dur / out_dur) if in_dur and out_dur else 1.0

        size_d = "-" if abs(out_mb - in_mb) < 0.05 else f"{out_mb - in_mb:+.1f} MB"
        scale_d = "-" if in_scale == out_scale else out_scale
        fps_d = (
            "-"
            if in_fps is None or out_fps is None or abs(out_fps - in_fps) < 0.05
            else f"{out_fps - in_fps:+.1f}"
        )
        speed_d = "-" if abs(out_speed - in_speed) < 0.05 else f"{out_speed - in_speed:+.1f}x"

        rows.append([
            (str(i), "input", src.name, f"{in_mb:.1f} MB", in_scale, f"{in_fps:.2f}" if in_fps else "?", f"{in_speed:.1f}x"),
            ("", "output", dest.name, f"{out_mb:.1f} MB", out_scale, f"{out_fps:.2f}" if out_fps else "?", f"{out_speed:.1f}x"),
            ("", "delta", "", size_d, scale_d, fps_d, speed_d),
        ])

    cols = ("#", "Role", "File", "Size", "Scale", "FPS", "Speed")
    widths = [4, 8, 28, 10, 12, 7, 7]
    rule = "-+-".join("-" * w for w in widths)

    def fmt(row: tuple[str, ...]) -> str:
        return " | ".join(f"{cell:<{w}}" for cell, w in zip(row, widths))

    print()
    print(fmt(cols))
    print(rule)
    for n, group in enumerate(rows):
        if n:
            print(rule)
        for row in group:
            print(fmt(row))
    print()


if __name__ == "__main__":
    main()
