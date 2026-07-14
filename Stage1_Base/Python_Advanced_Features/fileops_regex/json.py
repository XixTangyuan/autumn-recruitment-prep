import json
data={"name":"agent测试","code":200,"status":"正常"}  #字典数据
with open("data.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)  #json.dump()写入文件 json.dump(obj,fp,ensure_ascii=False,indent=None) #obj带序列化数据，python字典/列表 fp with open()打开的文件对象

with open("data.json","r",encoding="utf-8") as f:
    res=json.load(f)  #json.load()读取文件
print(res["name"])
