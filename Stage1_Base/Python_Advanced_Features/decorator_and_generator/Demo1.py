def outer(num1):
    #闭包函数
    def inner():
        nonlocal num1  #在比包内修改外部函数变量的值需要用 nonlocal 需要修改的外层变量
        num1=20  #修改外层变量
        result=num1+10  
        print(result)
    print("修改前：",num1)
    inner()
    print("修改后：",num1)
    return inner  #返回内部函数
f=outer(10)  #将外部函数赋值给f
f()  #运行f