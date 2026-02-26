"""Fallback content pipeline.
Order: Match -> Standings -> Qualification -> Stats -> Meme.
"""

from importlib import import_module

FALLBACK_ORDER = [
    "core.match_engine",
    "core.standings_engine",
    "core.qualification_engine",
    "core.stats_engine",
    "core.meme_engine",
]


def run_fallback_pipeline():
    for module_name in FALLBACK_ORDER:
        module = import_module(module_name)
        for fn_name in ("build_match_content", "build_standings_content", "build_qualification_content", "build_stats_content", "build_meme_content"):
            fn = getattr(module, fn_name, None)
            if callable(fn):
                print(f"🔁 Fallback trying: {module_name}")
                if fn():
                    print(f"✅ Fallback selected: {module_name}")
                    return True
                break

    print("❌ Fallback pipeline could not create content.")
    return False


if __name__ == "__main__":
    raise SystemExit(0 if run_fallback_pipeline() else 1)
