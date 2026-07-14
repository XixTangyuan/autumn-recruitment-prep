with open("test.txt","r",encoding="utf-8") as f:
    content = f.read()  #一次性读取全部内容
    print(content)

with open("test.txt","w",encoding="utf-8") as f:
    f.write("第一行测试文本\n第二行内容")  #覆盖写入

with open("test.txt","a",encoding="utf-8") as f:
    f.write("\n末尾新增一行")  #逐行读取

with open("test.txt","r",encoding="utf-8") as f:
    for line in f:#循环逐行读取，适配超大文件
        print(line.strip())