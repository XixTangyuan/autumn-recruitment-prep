import csv
import json
import re
from pathlib import Path

INPUT_CSV = Path(__file__).with_name("drug.csv")
OUTPUT_JSON = Path(__file__).with_name("structured_output.json")

def split_sentences(text: str) -> list[str]:
    if not text:
        return []
    parts = re.split(r'[。；\n]|(?=\d+\.)|(?<=\))', text)
    return [p.strip() for p in parts if p.strip()]

def normalize_category(text: str) -> str:
    if "解热" in text: return "解热"
    if "镇痛" in text: return "镇痛"
    if "心血管" in text or "心肌梗死" in text or "脑卒中" in text: return "心血管预防"
    if "抗炎" in text or "抗风湿" in text: return "抗炎抗风湿"
    return ""

def parse_indication_sentence(sentence: str) -> dict:
    disease_names = []
    for keyword in [
        "发热", "头痛", "肌肉痛", "关节炎", "风湿热", "急性风湿性关节炎",
        "心肌梗死", "脑卒中", "心绞痛", "深静脉血栓", "肺栓塞", "冠心病"
    ]:
        if keyword in sentence and keyword not in disease_names:
            disease_names.append(keyword)

    action = ""
    if "用于" in sentence:
        action = sentence.split("用于", 1)[1].split("。", 1)[0].strip()
    elif "治疗" in sentence:
        action = sentence

    return {
        "病症分类": normalize_category(sentence),
        "具体疾病名称": "；".join(disease_names),
        "治疗作用": action,
        "适用人群": "",
        "使用场景": "",
        "补充备注": sentence
    }

def parse_adverse_sentence(sentence: str) -> dict:
    category = ""
    if "胃肠道" in sentence or "恶心" in sentence or "呕吐" in sentence:
        category = "胃肠道反应"
    elif "过敏" in sentence or "皮疹" in sentence or "哮喘" in sentence:
        category = "过敏反应"
    elif "肝" in sentence:
        category = "肝损害"
    elif "肾" in sentence:
        category = "肾损害"
    elif "中枢神经" in sentence or "头痛" in sentence or "眩晕" in sentence:
        category = "中枢神经系统反应"
    elif "瑞氏综合征" in sentence:
        category = "瑞氏综合征"
    else:
        category = "其他不良反应"

    return {
        "不良反应类型": category,
        "症状描述": sentence,
        "补充备注": ""
    }

def build_structured_data(indication: str, adverse: str) -> dict:
    return {
        "indications": [
            item for sentence in split_sentences(indication)
            if (item := parse_indication_sentence(sentence)) and (item["具体疾病名称"] or item["治疗作用"] or item["病症分类"])
        ],
        "adverse_reactions": [
            parse_adverse_sentence(sentence)
            for sentence in split_sentences(adverse)
            if sentence
        ]
    }

def save_json(data: dict, output_path: Path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_source_data(csv_path: Path) -> list[dict]:
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

if __name__ == "__main__":
    rows = load_source_data(INPUT_CSV)
    structured_rows = []

    for row in rows:
        structured_rows.append({
            "title": row.get("title", ""),
            "source_indication": row.get("indication", ""),
            "source_adverse_reaction": row.get("adverse_reaction", ""),
            **build_structured_data(row.get("indication", ""), row.get("adverse_reaction", ""))
        })

    save_json(structured_rows, OUTPUT_JSON)
    print(f"Saved {len(structured_rows)} structured records to {OUTPUT_JSON}")