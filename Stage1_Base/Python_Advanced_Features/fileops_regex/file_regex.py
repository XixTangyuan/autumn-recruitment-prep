import re
import json
import os


#1. 模拟生成一份杂乱的日志文件
log_content = """
[2024-05-22 10:00:01] INFO: Server started on 192.168.1.100
[2024-05-22 10:05:23] ERROR: Connection timeout from 10.0.0.5 - User: admin
[2024-05-22 10:10:45] WARNING: High memory usage detected
[2024-05-22 10:15:12] ERROR: Database query failed from 192.168.1.105 - User: guest
Some random garbage text that we don't care about.
[2024-05-22 10:20:33] INFO: Backup completed successfully
"""
#将文本写入sever_log.txt文件
log_file="sever_log.txt"
with open(log_file,"w",encoding="utf-8") as f:
    f.write(log_content)
#读取文件内容
with open(log_file,"r",encoding="utf-8") as f:
    content=f.read()

# 2. 定义正则表达式提取关键信息
# 目标：提取 [时间] 级别: 详细信息
pattern=r"\[(.*?)\] (\w+):(.*)"

# 3. 读取文件并清洗数据
def parse_log(file_path):
    cleaned_data=[]
    with open(file_path,"r",encoding="utf-8") as f:
        for line in f:
            if not line:
                continue
            match=re.search(pattern,line)
            if match:#正则匹配后必须先校验
                timestamp,level,message=match.groups() #group()返回字符串，获取整行命令中的全部文本 group(数字)返回单个字符串，按需单独拿某一个分组 groups()返回元组tuple，一次性取出所有括号分组
                # 只保留 ERROR 和 WARNING 级别的日志
                if level in ["ERROR","WARNING"]:
                    cleaned_data.append({"timestamp":timestamp,"level":level,"message":message})
    return cleaned_data

# 4. 将清洗后的数据保存为 JSON
if __name__=="__main__":
    result=parse_log(log_file)
    output_file="cleaned_file.json"

    # 保存为 JSON 文件
    with open(output_file,"w",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
    print(f"\n清洗完成！共提取{len(result)}条关键日志，已保存至{output_file}")

    # 清理测试文件
    #os.remove(log_file)

