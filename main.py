import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent
INPUT_FILE = ROOT_DIR / "res" / "video.txt"
OUTPUT_DIR = ROOT_DIR / "video"


def sanitize_filename(name: str) -> str:
    """Convert a raw name to a filesystem-friendly filename stem."""
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"_+", "_", name).strip("._")
    return name or "video"


def filename_from_url(url: str, index: int) -> str:
    parsed = urlparse(url)
    path_name = Path(parsed.path).name
    stem = Path(path_name).stem
    stem = sanitize_filename(stem)
    # Prefix with sequence so names are stable and easy to read.
    return f"{index:02d}_{stem}.mp4"


def read_urls(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    urls: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        urls.append(item)
    return urls


def download_with_ffmpeg(url: str, output_file: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        url,
        "-c",
        "copy",
        str(output_file),
    ]
    subprocess.run(cmd, check=True)


def main() -> int:
    try:
        urls = read_urls(INPUT_FILE)
    except FileNotFoundError as exc:
        print(exc)
        return 1

    if not urls:
        print(f"No URL found in {INPUT_FILE}")
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = len(urls)
    for i, url in enumerate(urls, start=1):
        output_name = filename_from_url(url, i)
        output_file = OUTPUT_DIR / output_name
        print(f"[{i}/{total}] Downloading -> {output_file.name}")
        try:
            download_with_ffmpeg(url, output_file)
        except FileNotFoundError:
            print("ffmpeg not found. Please install ffmpeg and ensure it is in PATH.")
            return 1
        except subprocess.CalledProcessError as exc:
            print(f"Failed: {url}")
            print(f"ffmpeg exit code: {exc.returncode}")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
