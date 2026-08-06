"""Live Chinese meeting captioning + translation — terminal mode.

Runs the shared pipeline (pipeline.py) and prints captions to the console.
For the browser version, run `python web_app.py` instead.
"""

import sys

from pipeline import listen, TARGET_LANGUAGE


def main():
    print("Listening... (Ctrl+C to stop)\n")
    try:
        for event in listen():
            if event["type"] == "caption":
                print(f"ZH: {event['zh']}")
                print(f"{TARGET_LANGUAGE[:2].upper()}: {event['en']}\n")
            elif event["type"] == "error":
                print(f"({event['message']})\n")
    except KeyboardInterrupt:
        print("\nStopping...")
        sys.exit(0)


if __name__ == "__main__":
    main()
