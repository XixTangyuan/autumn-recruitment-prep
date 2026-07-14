import unittest
import os
import json
from robust import LogCleaner

class TestLogCleaner(unittest.TestCase):
    def setUp(self):
        self.test_log_file="test_sever_log.txt"
        self.test_output_file="test_cleaned_logs.json"
    
    # 创建测试日志文件
        log_content = """[2024-05-22 10:00:01] INFO: Server started
[2024-05-22 10:05:23] ERROR: Connection timeout
[2024-05-22 10:10:45] WARNING: High memory usage
"""
        with open(self.test_log_file,"w",encoding="utf-8")as f:
            f.write(log_content)
        self.cleaner=LogCleaner(log_level1="ERROR",log_level2="WARNING")
    
    def tearDown(self):
        if os.path.exists(self.test_log_file):#判断文件路径/文件夹是否存在
            os.remove(self.test_log_file)#如果在移除该文件
        if os.path.exists(self.test_output_file):
            os.remove(self.test_output_file)
    
    def test_parse_file(self):#测试parse_file方法是否能正确提取ERROR和WARNING
        result=self.cleaner.parse_file(self.test_log_file)#调用清洗方法得出结果,结果返回是个列表，里面的元素是字典类型
        self.assertEqual(len(result),2)
        self.assertEqual(result[0]["level"],"ERROR") 
        self.assertEqual(result[1]["level"],"WARNING")

    def test_save_to_json(self):#测试save_to_json是否正确地保存文件
        self.cleaner.parse_file(self.test_log_file)
        self.cleaner.save_to_json(self.test_output_file)
        self.assertTrue(os.path.exists(self.test_output_file))
        with open(self.test_output_file,"r",encoding="utf-8")as f:
            data=json.load(f)
        self.assertEqual(len(data),2)

    def test_parse_nonexistent_file(self):#测试读取不存在的文件时是否能优雅处理
        result=self.cleaner.parse_file("nonexistent_file.txt")#不存在的文件
        self.assertEqual(result,[])
    
if __name__=="__main__":
    unittest.main()