import sys
import json
import os
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
DAILY_DIR = os.path.join(SCRIPT_DIR, "daily")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")


def finish():
    word_count = input("오늘 쓴 글자수? ")
    word_count = int(word_count)

    difficulty = input("체감 난이도? (★/★★/★★★) ")

    summary = input("장면 한줄 요약? ")

    today = date.today().isoformat()
    daily_data = {
        "date": today,
        "word_count": word_count,
        "difficulty": difficulty,
        "summary": summary,
    }

    daily_path = os.path.join(DAILY_DIR, f"{today}.json")
    with open(daily_path, "w", encoding="utf-8") as f:
        json.dump(daily_data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    config = load_config()
    config["total_written"] += word_count
    save_config(config)

    total = config["total_written"]
    goal = config["monthly_goal"]
    percent = total / goal * 100
    print(f"오늘 글자수: {word_count} | 누적: {total} / {goal} ({percent:.0f}%)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python manager.py finish")
        sys.exit(1)

    command = sys.argv[1]
    if command == "finish":
        finish()
    else:
        print(f"알 수 없는 명령: {command}")
        sys.exit(1)
