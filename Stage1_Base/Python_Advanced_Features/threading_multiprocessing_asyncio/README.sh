##Python并发编程、GIL锁学习
1、GIL锁：在多线程里，其中一个线程执行时会上GIL锁，当发生IO阻塞时，打开GIL锁，其他线程可开始执行
2、IO密集型并发量小时用threading，并发量大时用asyncio;CPU密集型用multiprocessing
##关键字
import threading
#创建子线程 threading.Thread(target=函数名，args=(参数1，)   #启动线程 t.start()  #等待子线程全部跑玩汇合 t.join()
import multiprocessing
#创建子线程 multiprocessing.Process(target=函数名,args=(参数1)  #启动线程 p.start()  #等待子线程全部跑玩汇合 p.join()
import asyncio
#定义协程函数，返回协程对象  async def async_fetch():  #把协程函数打包为异步任务，放进循环队列 create_task(协程函数（））  #碰到await事件循环开始，激活所有队列里的任务 result=await t1 ;result=await asyncio.gather(task1(),task2()) 以列表形式呈现  #创建并启动事件循环 asyncio.run(main())  #在想要异步的编码前面添加await 后面的对象必须是一个可等待对象，如协程对象、Future对象等
##今日踩坑记录
1、线程启动语法错误
传入任务函数错误带上括号 target=func()，代码直接主线程执行完毕，没有创建子线程。正确写法：只写函数名，target=func,参数单独args传参
args传参格式写错，单个参数末尾缺少逗号args(1)报错，正确：args=(1,)

