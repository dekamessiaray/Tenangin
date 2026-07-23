
import os
import base64
import functools

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


@functools.lru_cache(maxsize=8)
def get_base64(filename: str) -> str:
    path = os.path.join(_ASSETS_DIR, filename)
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def logo_data_uri(filename: str = "logo_nav.png") -> str:
    return f"data:image/png;base64,{get_base64(filename)}"


def logo_path(filename: str = "logo_pdf.png") -> str:
    return os.path.join(_ASSETS_DIR, filename)
