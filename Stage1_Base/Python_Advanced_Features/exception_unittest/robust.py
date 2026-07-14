import re
import json
import os


#声明类
class LogCleaner:
    #构造函数__init__
    def __init__(self,log_level1,log_level2,log_pattern=r"\[(.*?)\] (\w+):(.*)"):
        self.log_pattern=log_pattern#实例属性
        self.log_level1=log_level1
        self.log_level2=log_level2
        self.cleaned_data=[] #实例对象专属容器，存放筛选后的日志
    
    def parse_file(self,file_path):#读取文件并清洗
        self.cleaned_data=[]#每次清洗前先清空旧数据
        try:
            with open(file_path,"r",encoding="utf-8") as f:
                for line in f:
                    if not line:
                        continue
                    match=re.search(self.log_pattern,line)
                    if match:
                        timestamp,level,message=match.groups()
                        if level in [self.log_level1,self.log_level2]:
                            self.cleaned_data.append({"timestamp":timestamp,"level":level,"message":message})
        except FileNotFoundError:
            print(f"错误：文件{file_path}不存在，请检查路径！")
        except PermissionError:
            print(f"没有权限读取文件{file_path}")
        except Exception as e:
            print(f"文件发生未知异常{e}")
        finally:
            print(f"共提取{len(self.cleaned_data)}条关键日志")
        return self.cleaned_data
    
    def save_to_json(self,output_file):#将清洗的数据保存到json文件里
        try:
            with open(output_file,"w",encoding="utf-8") as f:
                json.dump(self.cleaned_data,f,ensure_ascii=False,indent=2)
        except Exception as e:
            print(f"保存失败：{e}")
        else:
            print(f"清洗完成！已保存至{output_file}")


log_file="sever_log.txt"

if __name__=="__main__":
    #创建实例对象
    cleaner=LogCleaner(log_level1="ERROR",log_level2="WARNING")
    #传入日志文件并清洗数据
    cleaner.parse_file(log_file)
    #调用方法将清洗好的数据导出json
    cleaner.save_to_json("cleaned_log_opp.json")

    #创建实例对象
    cleaner2=LogCleaner(log_level1="INFO",log_level2=None)
    #传入日志文件并清洗数据
    cleaner2.parse_file(log_file)
     #调用方法将清洗好的数据导出json
    cleaner2.save_to_json("cleaned_log_opp2.json")

    #调用方法将qing
    #清理测试文件
    #os.remove(log_file)