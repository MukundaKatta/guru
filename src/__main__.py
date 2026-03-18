"""CLI for guru."""
import sys, json, argparse
from .core import Guru

def main():
    parser = argparse.ArgumentParser(description="Guru — AI Teaching Assistant. Automates grading, generates lesson plans, and answers student questions.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Guru()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.generate(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"guru v0.1.0 — Guru — AI Teaching Assistant. Automates grading, generates lesson plans, and answers student questions.")

if __name__ == "__main__":
    main()
