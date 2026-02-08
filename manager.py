import json
import os
import sys
from datetime import date

import anthropic

SCENES_DIR = "scenes"
DAILY_DIR = "daily"
HIGHLIGHTS_FILE = "highlights.json"
CONFIG_FILE = "config.json"

SYSTEM_PROMPT = "너는 소설 편집자야. 장면을 분석해서 정확히 아래 형식으로만 답변해."

USER_PROMPT = """다음 장면을 분석해줘:

{scene_text}

아래 형식으로만 답변:
요약: [한 줄 요약]
역할: [관계 진전/정보 공개/갈등 심화/전환/여운/리듬 유지 중 정확히 하나]
탁월: [있음/없음]
탁월타입: [대사/분위기/구조/관계성/캐릭터 - 탁월이 있음일 때만]
탁월이유: [한 줄 - 탁월이 있음일 때만]"""


def _load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_json(path, data):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_highlights():
    if os.path.exists(HIGHLIGHTS_FILE):
        with open(HIGHLIGHTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _parse_response(text):
    """API 응답을 줄별로 파싱하여 딕셔너리로 반환한다."""
    result = {}
    for line in text.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def _analyze_scene(scene_text):
    """Anthropic API를 호출하여 장면을 분석한다."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": USER_PROMPT.format(scene_text=scene_text),
            }
        ],
    )
    return _parse_response(message.content[0].text)


def finish(filename):
    """장면 파일을 읽고 분석하여 기록을 완료한다."""
    # 1. scenes/ 폴더에서 파일 찾기
    filepath = os.path.join(SCENES_DIR, filename)
    if not os.path.exists(filepath):
        print(f"오류: scenes/{filename} 파일을 찾을 수 없습니다.")
        sys.exit(1)

    # 2. 파일 읽기 + 글자수 계산
    with open(filepath, "r", encoding="utf-8") as f:
        scene_text = f.read()
    word_count = len(scene_text)

    # 3. Anthropic API 호출
    analysis = _analyze_scene(scene_text)

    summary = analysis.get("요약", "")
    role = analysis.get("역할", "")
    is_highlight = analysis.get("탁월", "없음") == "있음"
    highlight_type = analysis.get("탁월타입", "")
    highlight_reason = analysis.get("탁월이유", "")

    # 4. 분석 결과 출력
    print("장면 자동 분석 완료:")
    print(f"- 글자수: {word_count}자")
    print(f"- 요약: {summary}")
    print(f"- 역할: {role}")

    # 5. 체감 난이도 입력
    effort_input = input("\n체감 난이도 (1/2/3): ").strip()
    effort_map = {"1": "★", "2": "★★", "3": "★★★"}
    effort = effort_map.get(effort_input, "★")

    # 6. daily/YYYY-MM-DD.json 저장
    today = date.today().isoformat()
    os.makedirs(DAILY_DIR, exist_ok=True)
    daily_path = os.path.join(DAILY_DIR, f"{today}.json")
    daily_data = {
        "date": today,
        "word_count": word_count,
        "effort": effort,
        "summary": summary,
        "role": role,
        "scene_file": filename,
    }
    _save_json(daily_path, daily_data)

    # 7. 탁월 포인트가 있으면 highlights.json에 추가
    if is_highlight:
        highlights = _load_highlights()
        highlights.append({
            "date": today,
            "type": highlight_type,
            "location": summary,
            "memo": highlight_reason,
        })
        _save_json(HIGHLIGHTS_FILE, highlights)

    # 8. config.json의 total_written 업데이트
    config = _load_json(CONFIG_FILE)
    total_written = config.get("total_written", 0) + word_count
    config["total_written"] = total_written
    _save_json(CONFIG_FILE, config)

    # 9. 최종 출력
    goal = config.get("goal", 30000)
    pct = total_written / goal * 100

    print(f"\n✓ 저장 완료: daily/{today}.json")
    print(f"[{role}] {word_count}자 | 누적: {total_written} / {goal} ({pct:.0f}%)")

    if is_highlight:
        print(f"✓ [탁월 포인트] {highlight_type}: {highlight_reason}")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] != "finish":
        print("사용법: python manager.py finish [파일명]")
        print("예: python manager.py finish 001_나비-선우_첫_대화.txt")
        sys.exit(1)

    finish(sys.argv[2])
