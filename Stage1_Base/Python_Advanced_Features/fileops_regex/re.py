import re

#全提取findall
text1="IP:192.168.1.100、10.0.0.5"
res=re.findall(r"IP:((?:\d{0,3}\.){3}\d{0,3})",text1)
print(res)

#搜索全文中第一个匹配的内容search
text2="[2024-05-22 10:05:23] ERROR:Connection timeout"
res=re.search(r"\[(.*?)\] (\w+):",text2)
if res:
    time=res.group(1)
    level=res.group(2)
    print(time,level)

#清洗替换sub
text3="时间[2024-05-22]无用垃圾文字"
res=re.sub(r"\[.*?\]","",text3)
print(res)