#!/usr/bin/env python3
"""WriterOps 집필 관리 도구."""

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DAILY_DIR = BASE_DIR / "daily"
REPORTS_DIR = BASE_DIR / "reports"


def get_week_range(target_date=None):
    """주어진 날짜가 속한 주의 월요일~일요일 범위를 반환한다."""
    if target_date is None:
        target_date = date.today()
    monday = target_date - timedelta(days=target_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday, sunday


def iso_week_label(target_date=None):
    """ISO 주차 라벨을 반환한다 (예: 2026-W06)."""
    if target_date is None:
        target_date = date.today()
    iso_year, iso_week, _ = target_date.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def load_daily_files(monday, sunday):
    """월요일~일요일 범위에 해당하는 daily JSON 파일들을 읽어온다."""
    entries = []
    current = monday
    while current <= sunday:
        filepath = DAILY_DIR / f"{current.isoformat()}.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                entries.append(data)
        current += timedelta(days=1)
    return entries


def build_weekly_report(target_date=None):
    """주간 리포트 데이터를 생성한다."""
    monday, sunday = get_week_range(target_date)
    week_label = iso_week_label(monday)
    entries = load_daily_files(monday, sunday)

    total_days = 7
    writing_days = len(entries)
    rest_days = total_days - writing_days

    total_chars = sum(e.get("char_count", 0) for e in entries)
    avg_chars = total_chars // writing_days if writing_days > 0 else 0

    # 체감 난이도 분포
    difficulty_map = {1: 0, 2: 0, 3: 0}
    for e in entries:
        d = e.get("difficulty", 1)
        if d in difficulty_map:
            difficulty_map[d] += 1

    # 장면 역할 분포
    role_counter = {}
    for e in entries:
        role = e.get("scene_role", "")
        if role:
            role_counter[role] = role_counter.get(role, 0) + 1

    # 긴급 모드 횟수
    emergency_count = sum(1 for e in entries if e.get("emergency_mode", False))

    return {
        "week_label": week_label,
        "monday": monday.isoformat(),
        "sunday": sunday.isoformat(),
        "writing_days": writing_days,
        "rest_days": rest_days,
        "total_chars": total_chars,
        "avg_chars": avg_chars,
        "difficulty": difficulty_map,
        "scene_roles": role_counter,
        "emergency_count": emergency_count,
    }


def format_report(report):
    """리포트 딕셔너리를 터미널/파일 출력용 문자열로 변환한다."""
    difficulty_labels = {1: "★  ", 2: "★★ ", 3: "★★★"}
    sep = "=" * 30

    lines = []
    lines.append(f"=== 주간 리포트 ({report['week_label']}) ===")
    lines.append(
        f"집필: {report['writing_days']}일 / 휴식: {report['rest_days']}일"
    )
    lines.append(
        f"총 글자수: {report['total_chars']}자 (평균 {report['avg_chars']}자/일)"
    )
    lines.append("")
    lines.append("체감 난이도:")
    for level in (1, 2, 3):
        count = report["difficulty"].get(level, 0)
        lines.append(f"  {difficulty_labels[level]}: {count}일")
    lines.append("")
    lines.append("장면 역할:")
    for role, count in report["scene_roles"].items():
        lines.append(f"  {role}: {count}회")
    lines.append("")
    lines.append(f"긴급 모드: {report['emergency_count']}회")
    lines.append(sep)

    return "\n".join(lines)


def save_report(report, text):
    """리포트를 reports/ 디렉터리에 마크다운 파일로 저장한다."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"weekly_{report['week_label']}.md"
    filepath = REPORTS_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    return filepath


def cmd_weekly():
    """weekly 명령: 이번 주 주간 리포트를 생성한다."""
    if not DAILY_DIR.exists():
        print("daily/ 디렉터리가 존재하지 않습니다.")
        sys.exit(1)

    report = build_weekly_report()
    text = format_report(report)

    # 터미널 출력
    print(text)

    # 파일 저장
    filepath = save_report(report, text)
    print(f"\n리포트 저장: {filepath}")


def main():
    commands = {
        "weekly": cmd_weekly,
    }

    if len(sys.argv) < 2:
        print(f"사용법: python manager.py <command>")
        print(f"명령어: {', '.join(commands.keys())}")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd not in commands:
        print(f"알 수 없는 명령어: {cmd}")
        print(f"명령어: {', '.join(commands.keys())}")
        sys.exit(1)

    commands[cmd]()


if __name__ == "__main__":
    main()
