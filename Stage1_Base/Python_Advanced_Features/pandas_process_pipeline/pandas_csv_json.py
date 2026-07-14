import pandas as pd
import numpy as np

# 1. 模拟生成一份包含 3 种药品的“脏”数据 (实际业务中这是爬虫输出的 raw_data.csv)
raw_data = {
    "drug_name": ["阿司匹林", "布洛芬", "对乙酰氨基酚"],
    "indication": [
        "用于缓解轻度或中度疼痛，如头痛、牙痛。也用于感冒或流感引起的发热。",
        "缓解轻至中度疼痛如头痛、关节痛、偏头痛、牙痛、肌肉痛、神经痛、痛经。也用于普通感冒或流行性感冒引起的发热。",
        np.nan  # 模拟缺失值
    ],
    "adverse_reaction": [
        "1. 胃肠道反应：恶心、呕吐、上腹部不适。 2. 过敏反应：皮疹、荨麻疹。 <span class='edit'>编辑</span>",
        "少数病人可出现恶心、呕吐、胃烧灼感或轻度消化不良、胃肠道溃疡及出血、转氨酶升高。",
        "偶见皮疹、荨麻疹、药热及白细胞减少等不良反应。长期大量用药会导致肝肾功能异常。[播报]"
    ],
    "extract_time": ["2023-10-01 10:00:00", "2023-10-01 10:05:00", "2023-10-01 10:10:00"]
}

df_raw = pd.DataFrame(raw_data)
df_raw.to_csv("raw_drugs.csv", index=False, encoding="utf-8-sig")# 导出csv，不保存行索引，中文不乱码
print("模拟脏数据已生成：raw_drugs.csv")

# ================= Pandas 基础操作 =================

# 2. 读取 CSV
df = pd.read_csv("raw_drugs.csv")

# 3. 快速查看数据概况 (面试常问：你拿到数据第一步做什么？)
print("\n--- 数据基本信息 ---")
print(df.info())       # 查看列类型、非空值数量 (发现 indication 有缺失)
print(df.head(2))      # 查看前两行

# 4. 格式转换：CSV 转 JSON
# 在对接后端 API 或大模型时，JSON 是最常用的格式
df.to_json("drugs_standard.json", orient="records", force_ascii=False, indent=2)
print("\n 数据已转换为标准 JSON 格式：drugs_standard.json")
