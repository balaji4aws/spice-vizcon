"""Headless smoke test: run every chapter via Streamlit AppTest and assert no exceptions.

Usage:  python3 test_app.py      (exits 0 on success, 1 on any failure)
"""
import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent / "app.py"

SECTIONS = [
    "🏠 Start here",
    "① The Great Spice Boom",
    "② Grown There, Eaten Here",
    "③ Up in Smoke",
    "🧭 Assumptions & analysis",
    "📎 Sources & credits",
]


def run(section: str) -> bool:
    """Render one chapter headlessly. Returns True if it raised no exception."""
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.run()
    # select the chapter via the sidebar radio
    at.radio[0].set_value(section).run()
    if at.exception:
        print(f"[FAIL] {section}")
        for e in at.exception:
            print("   ", e.value)
        return False
    print(f"[ok]   {section}  (markdowns={len(at.markdown)})")
    return True


def main() -> int:
    results = [run(s) for s in SECTIONS]
    passed, total = sum(results), len(results)
    if all(results):
        print(f"\nALL PASS ({passed}/{total} chapters)")
        return 0
    print(f"\nFAILURES PRESENT ({total - passed}/{total} chapters failed)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
