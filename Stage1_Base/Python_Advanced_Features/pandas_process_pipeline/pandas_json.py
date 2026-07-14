import pandas as pd
import json
import re

df = pd.read_csv("cleaned_drugs.csv")

# ================= 1. 复杂数据转换 (Apply 与自定义函数) =================
# 业务场景：将“不良反应”长文本，按句号或序号拆分成列表（List），方便前端展示或 RAG 细粒度检索。

#def split_adverse_reactions(text):
#    if not isinstance(text, str):
#        return []
    # 按中文句号、数字编号(如 1. 2.) 进行拆分
    # 正则解释：(?=\d+\.) 是正向先行断言，按数字编号切分但不消耗编号
#    parts = re.split(r'。|(?=\d+\.)', text)
    # 过滤掉空字符串，并去除首尾空格
#    return [p.strip() for p in parts if p.strip()]

# 使用 apply 将函数应用到每一行，生成一个新的列（类型为 List）
#df['adverse_list'] = df['adverse_reaction'].apply(split_adverse_reactions)#.apply(func)：逐行遍历，把单元格值传给函数

# 向量化替代 apply 的实现（替换原来的 split_adverse_reactions + apply）
s = df['adverse_reaction'].fillna('').astype(str).str.strip()
# 按中文句号或数字编号拆分（正则保留编号边界）
split_ser = s.str.split(r'。|(?=\d+\.)')
# 展开成单条记录，逐项去空格并过滤空串
exploded = split_ser.explode().astype(str).str.strip()
exploded = exploded[exploded != '']
# 按原索引聚合回列表（每行一个 list）
adverse_lists = exploded.groupby(level=0).agg(list)
# 重新对齐原数据索引，缺失填空列表
df['adverse_list'] = adverse_lists.reindex(df.index).apply(lambda x: x if isinstance(x, list) else [])

# ================= 2. 构建 RAG 友好的数据结构 =================
# 大模型微调或 RAG 知识库导入，通常使用 JSONL 格式（每行一个独立的 JSON 对象）

rag_data = []
for index, row in df.iterrows():
    # 为每个药品构建 Metadata (元数据)，这在 RAG 检索时非常关键！
    metadata = {
        "drug_name": row['drug_name'],
        "category": "解热镇痛药", # 模拟业务分类
        "has_gi_reaction": row['gi_symptoms'] != "无" # 布尔值标签
    }
    
    # 将适应症和不良反应分别作为独立的 Document 存入，提高检索精度
    rag_data.append({
        "text": f"药品 {row['drug_name']} 的适应症为：{row['indication']}",
        "metadata": {**metadata, "section": "适应症"}
    })
    
    # 将拆分后的不良反应列表，逐条存入（细粒度 Chunking）
    for i, symptom in enumerate(row['adverse_list']):
        rag_data.append({
            "text": f"药品 {row['drug_name']} 的第 {i+1} 项不良反应为：{symptom}",
            "metadata": {**metadata, "section": "不良反应", "chunk_id": i}
        })

# ================= 3. 导出为 JSONL =================
output_jsonl = "drugs_rag_ready.jsonl"
with open(output_jsonl, 'w', encoding='utf-8') as f:
    for item in rag_data:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

print(f"✅ 成功生成 RAG 友好型数据：{output_jsonl}，共 {len(rag_data)} 个 Chunks。")
