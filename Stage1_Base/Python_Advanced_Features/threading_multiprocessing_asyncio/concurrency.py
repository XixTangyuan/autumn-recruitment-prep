import time
import threading
import multiprocessing
import asyncio

#模拟网路IO耗时操作
def fetch_url(url):
    time.sleep(1)
    return f"请求完成：{url}"

#1、普通串行顺序执行
def serial_demo(url_list):
    begin=time.time()
    for url in url_list:
        fetch_url(url)
    print(f"【串行执行总耗时】：{time.time()-begin:.2f}秒")

#2、threading多线程执行#适用于IO密集型任务
def thread_demo(url_list):
    begin=time.time()
    thread_group=[]
    for url in url_list:
        t=threading.Thread(target=fetch_url,args=(url,))  #threading.Thread 手动创建子线程，实现并行并发 target=函数名（线程要执行的任务函数，只写函数名） args=(参数1,)(给任务函数传参，元组格式，单个参数后面必须加逗号)
        thread_group.append(t)  #给thread_group里添加元素t
        t.start()  #启动线程
    for t in thread_group:
        t.join()  #等待子线程全部跑完汇合
    print (f"【多线程执行总耗时】：{time.time()-begin:.2f}秒")

#3、多进程执行#适用于CPU密集型任务
def process_demo(url_list):
    begin=time.time()
    process_group=[]
    for url in url_list:
        p=multiprocessing.Process(target=fetch_url,args=(url,))  #multiprocessing.Process 创建子进程实现真多核并行运算
        process_group.append(p)
        p.start()  #启动进程
    for p in process_group:
        p.join()  #等待子线程全部跑完汇合
    print (f"【多进程执行总耗时】：{time.time()-begin:.2f}秒")
    
#4、asyncio异步协程
async def async_fetch(url):
    await asyncio.sleep(1)
    return f"异步请求完成：{url}"

async def async_demo(url_list):
    begin=time.time()
    task_list=[async_fetch(url) for url in url_list]
    await asyncio.gather(*task_list)
    print (f"【asyncio异步总耗时】：{time.time()-begin:.2f}秒")

if __name__=="__main__":
    #模拟10条网络请求任务
    test_urls=[f"api/test/{i}"for i in range(10)]
    serial_demo(test_urls)
    thread_demo(test_urls)
    process_demo(test_urls)
    asyncio.run(async_demo(test_urls))