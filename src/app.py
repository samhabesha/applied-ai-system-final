"""
VibeFinder 2.0 command line.

  python -m src.app "upbeat songs for the gym, nothing too heavy"
  python -m src.app                 # interactive mode
  python -m src.app --offline ...   # force the offline path even if a key is set
  python -m src.app --debug ...     # also print profile, notes and guardrail events
"""

import argparse
import logging

from src.assistant import VibeFinder


def show(result, debug: bool) -> None:
    print(result.answer)
    if not result.blocked:
        print(f"\n[mode: {result.mode} | confidence: {result.confidence:.2f}]")
    if debug:
        print(f"profile: {result.profile}")
        print(f"notes retrieved: {result.notes}")
        print(f"guardrail events: {result.guardrail_events or 'none'}")


def main() -> None:
    ap = argparse.ArgumentParser(description="VibeFinder 2.0: RAG music recommender")
    ap.add_argument("query", nargs="*", help="your request; omit for interactive mode")
    ap.add_argument("--offline", action="store_true", help="do not call Claude")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO if args.debug else logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    vf = VibeFinder.create(offline=args.offline)
    if args.query:
        show(vf.ask(" ".join(args.query)), args.debug)
        return
    print(f"VibeFinder 2.0 ({vf.mode}). Describe what you want to hear; blank line to quit.")
    while True:
        try:
            query = input("\nyou> ").strip()
        except EOFError:
            break
        if not query:
            break
        show(vf.ask(query), args.debug)


if __name__ == "__main__":
    main()
