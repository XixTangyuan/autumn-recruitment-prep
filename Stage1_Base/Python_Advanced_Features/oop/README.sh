##核心知识点
1.类class:我们会把区有相同属性和能力的事物称为1个类，这样不用每创建一个对象都需要定义一遍属性和方法
语法：class LogCleaner:  #LogCleaner 是日志清洗工具模板
2.创建实例对象：cleaner=LogCleaner(实例属性1=赋值，实例属性2=赋值，...)
3.构造方法__inti__:创建实例对象时自动执行仅运行一次，初始化实例专属属性（正则模板、筛选日志等级、存储清洗结果的列表）
4.self：代表当前实例对象本身，类内所有实例方法，第一个参数强制写self
5.实例方法：parse_file(self, file_path)：读取日志文件、正则清洗、筛选指定等级日志；save_to_json(self, output_file)：将内存中清洗完成的数据导出为 JSON 文件
##实战项目：OOP 版日志清洗器 LogCleaner
1. 类完整功能
初始化自定义正则、两种需要筛选的日志等级；
读取本地日志文本，逐行正则提取「时间戳、日志级别、日志详情」；
自动过滤，仅保留配置的两种日志等级；
将结构化日志数据持久化导出为标准 JSON；
支持同时创建多个独立清洗实例，分别筛选不同日志类型。
2. 核心代码展示
import re
import json
import os

class LogCleaner:
    def __init__(self, log_pattern, log_level1, log_level2):
        # 绑定实例属性
        self.log_pattern = log_pattern
        self.log_level1 = log_level1
        self.log_level2 = log_level2
        self.cleaned_data = []

    def parse_file(self, file_path):
        self.cleaned_data = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                match = re.search(self.log_pattern, line)
                if match:
                    timestamp, level, message = match.groups()
                    # 筛选指定等级日志
                    if level in [self.log_level1, self.log_level2]:
                        self.cleaned_data.append({
                            "timestamp": timestamp,
                            "level": level,
                            "message": message
                        })
        return self.cleaned_data

    def save_to_json(self, output_file):
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.cleaned_data, f, ensure_ascii=False, indent=2)
        print(f"清洗完成！共提取 {len(self.cleaned_data)} 条关键日志，已保存至 {output_file}")

# 模拟日志生成、程序入口省略...
if __name__ == "__main__":
    # 实例1：筛选ERROR、WARNING报错日志
    cleaner = LogCleaner(r"\[(.*?)\] (\w+): (.*)", "ERROR", "WARNING")
    cleaner.parse_file("server_log.txt")
    cleaner.save_to_json("cleaned_log_oop.json")

    # 实例2：单独筛选INFO正常日志
    cleaner2 = LogCleaner(r"\[(.*?)\] (\w+): (.*)", "INFO", "INFO")
    cleaner2.parse_file("server_log.txt")
    cleaner2.save_to_json("cleaned_log_oop2.json")
3. 输出 JSON 示例
[
  {
    "timestamp": "2024-05-22 10:05:23",
    "level": "ERROR",
    "message": "Connection timeout from 10.0.0.5 - User: admin"
  },
  {
    "timestamp": "2024-05-22 10:10:45",
    "level": "WARNING",
    "message": "High memory usage detected"
  }
]
##踩坑壁坑总结
1.构造方法入参忘记绑定self.属性，跨方法读取变量提示未定义；
2.实例化时参数数量不匹配：无默认值的形参必须全部传入，少传直接抛TypeError；
3.混淆strip()与split()：split()会把字符串转为列表，re.search只能接收字符串，引发类型报错；
4.正则特殊符号[]未加\转义，匹配失效；
5.类方法忘记写第一个参数self，调用直接报错。
