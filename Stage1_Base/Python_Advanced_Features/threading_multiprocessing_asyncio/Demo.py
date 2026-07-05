import time

#模拟网络耗时5秒的IO操作
def task1():
    time.sleep(5)
    return 10

#模拟网络耗时3秒的IO操作
def task2():
    time.sleep(3)
    return 20

def main():
    result=task1()
    print("任务1执行结果：",result)
    result=task2()
    print("任务2执行结果：",result)

if __name__=="__main__":
    begin=time.time()
    main()
    print("总耗时：",time.time()-begin)