# 导入日志模块，用于打印运行信息、警告、错误
import logging
# 导入正则表达式，用于清洗文本多余空白、全角空格
import re
# 路径工具，用于生成csv文件路径
from pathlib import Path
# requests备用（当前代码未使用，保留兼容后续扩展）
import requests
# pandas用于将抓取结果保存为csv表格
import pandas as pd
# BeautifulSoup用于解析HTML页面，提取标签内容
from bs4 import BeautifulSoup
# requests网络异常类（当前未使用，兼容扩展）
from requests.exceptions import HTTPError, RequestException, Timeout
# 时间模块，用于延时等待、随机休眠
import time
# 随机数模块，生成随机休眠时长防反爬
import random
# playwright无头浏览器，加载百度百科动态渲染页面
from playwright.sync_api import sync_playwright

# 配置日志输出格式：时间-日志级别-日志内容
logging.basicConfig(
    level=logging.INFO,#INFO级别以上的都会显示
    format="%(asctime)s [%(levelname)s] %(message)s",#输出格式 #%(asctime)s 日志打印时间 %(levelname)s 日志级别名称 %(message)s 日志正文
    datefmt="%H:%M:%S",#时间格式
)
# 创建日志实例，区分爬虫日志
logger = logging.getLogger("baike_spider")

# 请求头，模拟真实浏览器访问，降低反爬拦截概率
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Referer": "https://baike.baidu.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}
# 目标百度百科药品词条链接
TARGET_URL = "https://baike.baidu.com/item/%E9%98%BF%E5%8F%B8%E5%8C%B9%E6%9E%97/15777"
# 输出csv文件路径，和当前脚本同目录
OUTPUT_CSV = Path(__file__).with_name("drug.csv")

# 文本清洗函数：去除多空格、全角空格，首尾去空
def clean_text(text: str) -> str:
    # 判断文本为空直接返回空字符串
    if not text:
        return ""
    # 将所有空白、全角空格统一替换为单个半角空格
    cleaned_text = re.sub(r"[\s\u3000]+", " ", text)#"[\s\u3000]+" 要替换的东西  " "替换成为的东西
    # 去除首尾空格后返回清洗完成文本
    return cleaned_text.strip()#strip()去除首位空格

# 使用playwright无头浏览器加载页面，返回完整渲染后的html源码
def fetch_page(url: str) -> str:
    logger.info("开始请求百度百科页面：%s", url)
    try:
        # 启动playwright浏览器上下文
        with sync_playwright() as p:
            # 后台无界面启动Chrome
            browser = p.chromium.launch(headless=True)
            # 创建浏览器上下文，注入浏览器UA伪装
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
            # 新建空白标签页
            page = context.new_page()
            # 先访问百度百科首页，模拟正常浏览行为
            page.goto("https://baike.baidu.com/", timeout=12000)
            # 等待2秒加载首页
            page.wait_for_timeout(2000)
            # 跳转目标药品词条页面，超时限制12秒
            page.goto(url, timeout=12000)
            # 等待3秒，等待页面动态DOM、词条正文渲染完成
            page.wait_for_timeout(3000)
            # 获取完整渲染后的页面HTML源码
            html = page.content()
            # 关闭浏览器释放资源
            browser.close()
            # 返回页面源码给解析函数
            return html
    # 捕获浏览器加载所有异常，打印错误日志并返回空字符串
    except Exception as e:
        logger.error("浏览器获取页面失败：%s", e)
        return ""

# 提取词条主标题
def extract_title(soup: BeautifulSoup) -> str:
    logger.info("开始提取词条标题")
    # 定义多个标题备选css选择器，兼容百科不同页面结构
    title_candidates = [
        "h1.lemmaWgt-lemmaTitle-title",
        "h1",
        ".lemmaWgt-lemmaTitle-title",
    ]
    # 循环遍历所有标题选择器
    for selector in title_candidates:
        # 根据选择器匹配第一个标题标签
        title_tag = soup.select_one(selector)
        # 判断成功匹配到标题标签
        if title_tag:
            # 提取标签内文本并清洗格式
            title_text = clean_text(title_tag.get_text(" ", strip=True))
            # 清洗后文本非空则返回标题
            if title_text:
                logger.info("成功提取标题：%s", title_text)
                return title_text
    # 所有选择器均未匹配标题，打印警告并返回空
    logger.warning("未提取到词条标题")
    return ""

# 通用章节提取函数：根据章节名（如适应症）提取对应正文
def extract_section_text(soup: BeautifulSoup, section_name: str) -> str:
    logger.info("开始提取章节内容：%s", section_name)
    # 初始化目标h2标题标签
    target_h2 = None
    # 遍历页面全部h2标签，匹配章节名称
    for h2 in soup.find_all("h2"):
        # 清洗h2内文本用于精准匹配
        h2_txt = clean_text(h2.get_text())
        # 当前h2文本等于目标章节名，记录该标签并跳出循环
        if h2_txt == section_name:
            target_h2 = h2
            break
    # 未找到对应章节h2，打印警告返回空文本
    if not target_h2:
        logger.warning(f"未找到章节标题：{section_name}")
        return ""

    # 获取当前章节下一个h2，作为章节内容结束边界
    next_h2 = target_h2.find_next("h2")
    # 列表存储所有抓取到的正文片段
    content_list = []

    # 从h2下一个DOM节点开始遍历，直至遇到下一个h2停止
    current = target_h2.next_element
    while current and current != next_h2:
        # 判断当前节点是div标签再处理
        if hasattr(current, "name") and current.name == "div":
            # 获取当前div全部class属性，无class返回空列表
            div_cls = current.get("class", [])
            # 严格校验div同时拥有三个指定class
            if "para_boGDy" in div_cls and "content_Qje75" in div_cls and "MARK_MODULE" in div_cls:
                # 在当前div内匹配指定class的正文span
                span_all = current.select('span.text__fK5J.J-lemma-content-lemma-text')
                # 遍历所有正文span，提取清洗文本
                for span in span_all:
                    span_txt = clean_text(span.get_text())
                    # 非空文本加入内容列表
                    if span_txt:
                        content_list.append(span_txt)
        # 移动到下一个DOM节点继续循环
        current = current.next_element

    # 列表为空代表没有抓取到章节正文
    if not content_list:
        logger.warning(f"{section_name} 未抓取到正文span内容")
        return ""
    # 拼接所有文本片段为完整段落
    full_text = "".join(content_list)
    logger.info(f"{section_name} 提取成功，文本长度：{len(full_text)}")
    return full_text


# 将抓取到的字典数据写入csv文件
def save_to_csv(data: dict, output_path: Path) -> None:
    logger.info("开始保存数据到 CSV 文件：%s", output_path)
    # 字典转为单行DataFrame表格
    df = pd.DataFrame([data])
    # 写入csv，不保存行索引，utf-8-sig兼容Excel中文不乱码
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info("数据已成功保存到 CSV 文件")

# 程序主执行入口
def main() -> None:
    logger.info("开始执行药品词条抓取任务")
    # 调用浏览器函数获取页面HTML源码
    html_text = fetch_page(TARGET_URL)
    # 页面源码为空，直接写入空数据csv
    if not html_text:
        logger.warning("页面内容为空，使用空值结果写入 CSV")
        result = {
            "title": "",
            "indication": "",
            "adverse_reaction": "",
        }
        save_to_csv(result, OUTPUT_CSV)
        return
    # 使用html.parser解析页面，生成soup对象用于标签查询
    soup = BeautifulSoup(html_text, "html.parser")
    # 调用函数提取词条标题
    title = extract_title(soup)
    # 提取适应症正文
    indication = extract_section_text(soup, "适应症")
    # 提取不良反应正文
    adverse_reaction = extract_section_text(soup, "不良反应")
    
    # 整合所有抓取字段为结果字典
    result = {
        "title": title or "",
        "indication": indication or "",
        "adverse_reaction": adverse_reaction or "",
    }
    logger.info("抓取结果已整理完成，准备写入 CSV")
    # 执行保存csv操作
    save_to_csv(result, OUTPUT_CSV)
    logger.info("全部任务完成，输出文件为：%s", OUTPUT_CSV)
    # 随机休眠2~4秒，模拟人工浏览，降低封禁风险
    time.sleep(random.uniform(2, 4))
    

# 脚本直接运行时启动主函数，被导入为模块时不自动执行
if __name__ == "__main__":
    main()
