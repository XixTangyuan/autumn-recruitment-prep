try:
    f=open("test123.txt","r",encoding="utf-8")
    content=f.readlines()
except FileNotFoundError:
    print("文件不存在")
else:
    print("文件读取正常")
finally:
    print("本次文件操作流程结束")