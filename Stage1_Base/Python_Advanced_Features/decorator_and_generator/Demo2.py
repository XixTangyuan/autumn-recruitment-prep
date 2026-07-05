#该装饰器可以成为通用装饰器
def decorator(func):  #使用装饰器装饰已有函数时，内部函数的类型和要装饰的函数的类型必须一致 #装饰器只能接受一个函数作为参数
    def inner(*args,**kwargs):  #*args,**kwargs #args:元组类型 kwaegs:字典类型
        result=func(*args,**kwargs)  #执行原函数，转发所有参数 #对元组和字典惊进行拆包，仅限于结合不定长参数的函数使用
        result1=result+20
        return
    return inner  #返回内部函数形成闭包函数
@decorator  #使用装饰器 等价于 comment=decorator(comment)
def comment(*args,**kwargs):
    result=0
    for i in args:
        result+=i
    for value in kwargs.values():
        result+=value
    print(result)
    return result

result=comment(10,20)  #执行comment函数 comment(10)=inner(10)
print("结果为：",result)  #打印修改后的结果