#!/usr/bin/env python3
"""WriterOps — 집필 세션 관리 도구."""

import json
import os
from datetime import date
from pathlib import Path

import anthropic

DAILY_DIR = Path(__file__).parent / "daily"

ROLE_OPTIONS = [
    "관계 진전",
    "정보 공개",
    "갈등 심화",
    "전환",
    "여운",
    "리듬 유지",
]


def _today_path() -> Path:
    return DAILY_DIR / f"{date.today().isoformat()}.json"


def _load_today() -> list[dict]:
    path = _today_path()
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def _save_today(records: list[dict]) -> None:
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    path = _today_path()
    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _ask(prompt: str, default: str = "") -> str:
    """입력을 받되, 빈 값이면 default 를 반환."""
    val = input(prompt).strip()
    return val if val else default


def _classify_role(summary: str) -> str:
    """Anthropic API를 호출하여 장면 요약에서 역할 태그를 자동 분류한다."""
    role_list = "\n".join(f"- {r}" for r in ROLE_OPTIONS)
    prompt = (
        f"이 장면 요약을 보고 역할 태그를 하나만 선택해줘:\n"
        f"{role_list}\n\n"
        f"장면 요약: {summary}\n\n"
        f"답변은 태그 이름만 정확히 하나만 출력해줘."
    )

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=32,
            messages=[{"role": "user", "content": prompt}],
        )
        role = message.content[0].text.strip()
        if role in ROLE_OPTIONS:
            return role
        return "미분류"
    except Exception as e:
        print(f"  (API 호출 실패: {e} → 미분류로 저장)")
        return "미분류"


def finish() -> None:
    """장면 마무리: 글자수·체감·한줄요약을 입력받고, 장면 역할은 자동 분류한다."""
    print("\n── 장면 마무리 ──\n")

    # 1) 글자수
    word_count_str = _ask("글자수? ")
    try:
        word_count = int(word_count_str)
    except ValueError:
        print("숫자를 입력해 주세요.")
        return

    # 2) 체감
    effort = _ask("체감? (예: ★★★) ")

    # 3) 한줄요약
    summary = _ask("한줄요약? ")

    # 4) 장면 역할 — API 자동 분류
    print("\n장면 역할 자동 분류 중...")
    role = _classify_role(summary)
    print(f"  → [자동: {role}]")

    # 레코드 저장
    record = {
        "date": date.today().isoformat(),
        "word_count": word_count,
        "effort": effort,
        "summary": summary,
        "role": role,
    }

    records = _load_today()
    records.append(record)
    _save_today(records)

    # 결과 출력
    _print_record(record)
    print(f"\n저장 완료 → {_today_path()}")


def _print_record(rec: dict) -> None:
    """레코드 한 건을 보기 좋게 출력."""
    print()
    print(f"  날짜     : {rec['date']}")
    print(f"  글자수   : {rec['word_count']}")
    print(f"  체감     : {rec['effort']}")
    print(f"  한줄요약 : {rec['summary']}")
    print(f"  장면 역할: [자동: {rec['role']}]")


def show() -> None:
    """오늘 기록을 모두 출력."""
    records = _load_today()
    if not records:
        print("오늘 기록이 없습니다.")
        return
    print(f"\n── {date.today().isoformat()} 기록 ──")
    for i, rec in enumerate(records, 1):
        print(f"\n[{i}]")
        _print_record(rec)


def main() -> None:
    import sys

    commands = {
        "finish": finish,
        "show": show,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(f"사용법: python manager.py <{'|'.join(commands)}>")
        return

    commands[sys.argv[1]]()


if __name__ == "__main__":
    main()
