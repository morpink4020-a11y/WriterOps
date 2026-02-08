import json
import os
from datetime import date

import anthropic

HIGHLIGHTS_FILE = "highlights.json"

EVALUATION_PROMPT = """다음 장면 요약을 보고 특출난 점이 있는지 판단해줘:
{scene_summary}

특출난 점 기준:
- 대사가 인상적
- 분위기/묘사가 탁월
- 구조/전개가 독창적
- 관계성 묘사가 뛰어남
- 캐릭터 표현이 생생함

답변 형식:
상태: 있음/없음
타입: 대사/분위기/구조/관계성/캐릭터 (있으면)
이유: 한 줄 (있으면)"""


def _load_highlights():
    if os.path.exists(HIGHLIGHTS_FILE):
        with open(HIGHLIGHTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_highlights(highlights):
    with open(HIGHLIGHTS_FILE, "w", encoding="utf-8") as f:
        json.dump(highlights, f, ensure_ascii=False, indent=2)


def _evaluate_scene(scene_summary: str) -> dict | None:
    """Anthropic API를 호출하여 장면의 특출난 점을 평가한다."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": EVALUATION_PROMPT.format(scene_summary=scene_summary),
            }
        ],
    )

    response_text = message.content[0].text
    lines = {}
    for line in response_text.strip().splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            lines[key.strip()] = value.strip()

    status = lines.get("상태", "없음")
    if status == "있음":
        return {
            "type": lines.get("타입", ""),
            "reason": lines.get("이유", ""),
        }
    return None


def finish(scene_summary: str):
    """장면 기록을 완료하고, 특출난 점이 있으면 highlights.json에 저장한다."""
    # 1. 장면 기록 완료
    print(f"장면 기록 완료: {scene_summary}")

    # 2. Anthropic API로 특출난 점 평가
    result = _evaluate_scene(scene_summary)

    # 3. '있음'이면 highlights.json에 자동 저장
    if result:
        highlight = {
            "date": date.today().isoformat(),
            "type": result["type"],
            "location": scene_summary,
            "memo": result["reason"],
        }

        highlights = _load_highlights()
        highlights.append(highlight)
        _save_highlights(highlights)

        # 4. 터미널에 표시
        print(f"✓ [탁월 포인트 발견] {result['type']}: {result['reason']}")
    else:
        print("— 특출난 점 없음")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: python manager.py <장면 요약>")
        sys.exit(1)

    finish(" ".join(sys.argv[1:]))
