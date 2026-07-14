import re
import json
import os


#声明类
class LogCleaner:
    #构造函数__init__
    def __init__(self,log_pattern,log_level1,log_level2):
        self.log_pattern=log_pattern#实例属性
        self.log_level1=log_level1
        self.log_level2=log_level2
        self.cleaned_data=[] #实例对象专属容器，存放筛选后的日志

    def parse_file(self,file_path):#读取文件并清洗
        self.cleaned_data=[]#每次清洗前先清空旧数据
        with open(file_path,"r",encoding="utf-8") as f:
            for line in f:
                if not line:
                    continue
                match=re.search(self.log_pattern,line)
                if match:
                    timestamp,level,message=match.groups()
                    if level in [self.log_level1,self.log_level2]:
                        self.cleaned_data.append({"timestamp":timestamp,"level":level,"message":message})
        return self.cleaned_data
    
    def save_to_json(self,output_file):#将清洗的数据保存到json文件里
        with open(output_file,"w",encoding="utf-8") as f:
            json.dump(self.cleaned_data,f,ensure_ascii=False,indent=2)
        print(f"清洗完成！已保存至{output_file}")

    def show_count(self):#打印当前筛选出来一共几条日志
        print(f"共提取{len(self.cleaned_data)}条关键日志")

#模拟生成一份杂乱的日志文件
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

if __name__=="__main__":
    #创建实例对象
    cleaner=LogCleaner(log_pattern=r"\[(.*?)\] (\w+):(.*)",log_level1="ERROR",log_level2="WARNING")
    #传入日志文件并清洗数据
    cleaner.parse_file(log_file)
    #调用方法将清洗好的数据导出json
    cleaner.save_to_json("cleaned_log_opp.json")
    cleaner.show_count()
    #创建实例对象
    cleaner2=LogCleaner(log_pattern=r"\[(.*?)\] (\w+):(.*)",log_level1="INFO",log_level2=None)
    #传入日志文件并清洗数据
    cleaner2.parse_file(log_file)
     #调用方法将清洗好的数据导出json
    cleaner2.save_to_json("cleaned_log_opp2.json")
    cleaner2.show_count()
    #调用方法将qing
    #清理测试文件
    #os.remove(log_file)