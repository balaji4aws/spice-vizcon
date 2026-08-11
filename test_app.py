"""Headless smoke test: run every chapter via Streamlit AppTest and assert no exceptions."""
from streamlit.testing.v1 import AppTest

SECTIONS = [
    "🏠 Start here",
    "① The Great Spice Boom",
    "② Grown There, Eaten Here",
    "③ Up in Smoke",
    "🧭 Assumptions & analysis",
    "📎 Sources & credits",
]

def run(section):
    at = AppTest.from_file("app.py", default_timeout=60)
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

if __name__ == "__main__":
    ok = all(run(s) for s in SECTIONS)
    print("\nALL PASS" if ok else "\nFAILURES PRESENT")
