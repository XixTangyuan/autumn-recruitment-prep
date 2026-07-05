import time #导入时间模块
#定义装饰器
def decorator(func):
    def inner(*args,**kwargs):
        begin=time.time()  #记录开始时间
        func(*args,**kwargs)  #执行原函数
        end=time.time()  #记录结束时间
        print("执行时间：",end-begin)
    return inner

@decorator  #使用装饰器 等价于 work=decorator(work)
def work():
    for i in range(10000):
        print(i)

if __name__=="__main__":
    ouput=work()  #执行work函数 work()=inner()