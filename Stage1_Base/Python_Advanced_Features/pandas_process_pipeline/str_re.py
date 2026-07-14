import pandas as pd
import re

df = pd.read_csv("raw_drugs.csv")

# ================= 1. 处理缺失值 =================
# 业务策略：对于缺失的适应症，我们可以填充为 "暂无数据"，或者直接丢弃该行。这里选择填充。
df['indication'] = df['indication'].fillna("暂无数据")
print("✅ 缺失值处理完成")

# ================= 2. 文本清洗 (去除脏字符) =================
# Pandas 的 .str 访问器可以对整列进行向量化字符串操作，比 for 循环快得多！

# 去除 HTML 标签残留 (如 <span class='edit'>编辑</span>)
# 正则解释：<[^>]+> 匹配所有尖括号内的内容
df['adverse_reaction'] = df['adverse_reaction'].str.replace(r'<[^>]+>', '', regex=True)

# 去除特定的干扰词 (如 [播报]、编辑)
df['adverse_reaction'] = df['adverse_reaction'].str.replace(r'\[播报\]|编辑', '', regex=True)

# 去除首尾多余的空格和换行
df['adverse_reaction'] = df['adverse_reaction'].str.strip()
print("✅ 文本脏字符清洗完成")

# ================= 3. 正则提取 (进阶) =================
# 假设业务需求：我们需要单独提取出阿司匹林不良反应中的“胃肠道”相关症状。
# 使用 str.extract 配合正则捕获组 ()

# 定义正则：匹配“胃肠道反应：”后面的内容，直到遇到句号或数字编号
pattern = r'胃肠道反应[：:](.*?)(?=\d\.|$)'
df['gi_symptoms'] = df['adverse_reaction'].str.extract(pattern, expand=False)

# 将提取不到的 NaN 填充为 "无"
df['gi_symptoms'] = df['gi_symptoms'].fillna("无")

print("\n--- 清洗与提取后的数据 ---")
print(df[['drug_name', 'adverse_reaction', 'gi_symptoms']])

# 保存清洗后的中间结果
df.to_csv("cleaned_drugs.csv", index=False, encoding="utf-8-sig")
