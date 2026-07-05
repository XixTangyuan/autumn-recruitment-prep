import time
import asyncio

#task1()任务有事件循环来管理调度，不由我们调度
async def task1():#协程函数，返回值不是直接的结果而是一个协程对象 #协程函数能够支持暂停和恢复执行但是普通函数不行
    #time.sleep(5)  #模拟网络耗时5秒的IO操作
    #await time.sleep(5)  #模拟网络耗时5秒的IO操作 #await关键字表示挂起当前协程，等待IO操作完成后再继续执行 #await 后面的对象必须是一个可等待对象（awaitable object），如协程对象、Future对象等
    await asyncio.sleep(5)  #模拟网络耗时5秒的IO操作 #time.sleep需要替换为async def 定义版本的sleep函数，asyncio.sleep()是异步版本的sleep函数，可以在协程中使用
    return 10

#模拟网络耗时3秒的IO操作
async def task2():
    await asyncio.sleep(3)
    return 20

async def main():
    #获得事件循环
    #loop=asyncio.get_event_loop()  不用手动获取loop
    #手动注册任务
    #t1=asyncio.create_task(task1())  #create_task()把协程打包为异步任务，自动并发执行，不会串行等待 #任务1进入循环队列等待执行
    #t2=asyncio.create_task(task2())  #任务2进入循环队列等待执行
    #等待任务1完成,并获得任务1的返回值
    #result1=await t1  #碰到await，事件循环开始，激活所有在队列里的任务，按照队列先后开始执行，等待前面任务挂起，开始执行下一个任务
    #print("任务1执行结果：",result1)
    #result2=await t2
    #print("任务2执行结果：",result2)
    result=await asyncio.gather(task1(),task2()) #以列表形式呈现
    print(result)

if __name__=="__main__":
    begin=time.time()
    #创建事件循环
    #loop=asyncio.get_event_loop()   不用手动获取loop
    #将协程对象注册到事件循环中，并启动事件循环
    #loop.run_until_complete(main())
    asyncio.run(main())
    print("总耗时：",time.time()-begin)