#!/usr/bin/env python3
"""WriterOps CLI manager for story and scene operations."""

import sys

from writerops.scene import save_scene


def read_multiline(prompt: str) -> str:
    """Read multiline input terminated by two consecutive blank lines."""
    print(prompt)
    lines = []
    blank_count = 0
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            blank_count += 1
            if blank_count >= 2:
                break
            lines.append(line)
        else:
            blank_count = 0
            lines.append(line)

    # Strip trailing blank lines
    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


def cmd_save_scene() -> None:
    title = input("장면 제목: ").strip()
    if not title:
        print("오류: 장면 제목을 입력해야 합니다.", file=sys.stderr)
        sys.exit(1)

    text = read_multiline("\n장면 텍스트 입력:")
    if not text:
        print("오류: 장면 텍스트를 입력해야 합니다.", file=sys.stderr)
        sys.exit(1)

    filepath = save_scene(title, text)
    print(f"\n장면이 저장되었습니다: {filepath}")


COMMANDS = {
    "save-scene": cmd_save_scene,
}


def main() -> None:
    if len(sys.argv) < 2:
        print(f"사용법: python {sys.argv[0]} <command>")
        print(f"사용 가능한 명령어: {', '.join(COMMANDS)}")
        sys.exit(1)

    command = sys.argv[1]
    if command not in COMMANDS:
        print(f"알 수 없는 명령어: {command}", file=sys.stderr)
        print(f"사용 가능한 명령어: {', '.join(COMMANDS)}")
        sys.exit(1)

    COMMANDS[command]()


if __name__ == "__main__":
    main()
