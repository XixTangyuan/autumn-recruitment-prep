#生成器
def big_date_generator(num):
    for i in range(num):
        yield i #yield关键字可以将函数变为生成器函数，返回一个迭代器对象

if __name__=="__main__":
    gen=big_date_generator(10000)
    for date in gen:
        if date % 100==0:
            print(date)


#逐行读取大文件的生成器函数
def read_file_generator(filr_path):
    with open(file_path,"r", encoding="UTF-8") as file:  #with open() as 打开文件后自动关闭，避免忘记关闭文件导致内存泄漏  #"r"表示只读模式，"w"表示写入模式，"a"表示追加模式，"b"表示二进制模式，"t"表示文本模式
        for line in file:
            yield line

if __name__=="__main__":
    file_path="test.txt"
    gen=read_file_generator(file_path)  #生成器对象
    for line in gen:
        print(line) #逐行读取大文件