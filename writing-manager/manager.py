import glob
import sys
import json
import os
from datetime import date

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
DAILY_DIR = os.path.join(SCRIPT_DIR, "daily")
SCENES_DIR = os.path.join(SCRIPT_DIR, "scenes")


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


def save_scene():
    title = input("장면 제목? ")

    print("장면 텍스트? (빈 줄 두 번 입력하면 종료)")
    lines = []
    empty_count = 0
    while True:
        line = input()
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
            lines.append(line)
        else:
            empty_count = 0
            lines.append(line)

    # 마지막 빈 줄 제거
    while lines and lines[-1] == "":
        lines.pop()

    text = "\n".join(lines)

    # 다음 번호 계산
    existing = glob.glob(os.path.join(SCENES_DIR, "*.txt"))
    next_num = len(existing) + 1

    # 파일명 생성: 공백과 특수문자를 _로 변환
    safe_title = title.replace(" ", "_").replace("-", "-")
    filename = f"{next_num:03d}_{safe_title}.txt"
    filepath = os.path.join(SCENES_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
        f.write("\n")

    char_count = len(text)
    print(f"저장 완료: scenes/{filename} ({char_count}자)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python manager.py [finish|save-scene]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "finish":
        finish()
    elif command == "save-scene":
        save_scene()
    else:
        print(f"알 수 없는 명령: {command}")
        sys.exit(1)
