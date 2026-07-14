import csv

with open("table.csv","r",encoding="utf-8") as f:
    reader=csv.DictReader(f)  #csv.DictReader()读取csv表格文件，自动把每一行数据转化为字典格式 字典key=csv第一行表头字段名 字典value=当前行对应单元格内容 
    #csv.DictReader(fp,fieldnames=None)  fp with open()打开得到的文件对象  fieldnames 自定义表头，csv文件第一行没有表头的时候手动设置表头名称，字典格式
    for row in reader:
        print(row["用户名"],row["IP地址"])