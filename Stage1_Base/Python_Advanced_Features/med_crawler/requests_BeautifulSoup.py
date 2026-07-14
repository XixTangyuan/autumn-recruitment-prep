"""
requests.get 核心参数 + BeautifulSoup4 解析示例

requests 文档: https://requests.readthedocs.io/en/latest/user/quickstart/
BeautifulSoup 文档: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
"""

import logging
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from requests.exceptions import HTTPError, RequestException, Timeout

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# 模拟真实浏览器，降低被反爬拦截的概率
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# PubMed 搜索页（静态 HTML 只有骨架，文献列表由 JS 异步加载）
PUBMED_SEARCH_URL = "https://pubmed.ncbi.nlm.nih.gov/"
# 用于演示 params 拼接的 httpbin 测试接口
HTTPBIN_GET_URL = "https://httpbin.org/get"


def fetch_with_params(
    url: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 10,
) -> requests.Response:
    """
    封装 requests.get，演示 headers / timeout / params 三参数协同使用。

    params 示例: {"term": "diabetes", "format": "abstract"}
    实际请求 URL: https://.../?term=diabetes&format=abstract
    """
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}

    logger.info("请求 URL 基址: %s", url)
    logger.info("查询参数 params: %s", params)

    response = requests.get(
        url,
        headers=merged_headers,
        params=params,
        timeout=timeout,
    )

    # params 由 requests 自动 URL 编码，可通过 response.url 查看最终地址
    logger.info("最终请求 URL: %s", response.url)
    return response


def handle_http_status(response: requests.Response) -> None:
    """按状态码区分 403 / 404 等 HTTP 异常。"""
    status = response.status_code

    if status == 403:
        raise HTTPError(
            f"403 Forbidden — 服务器拒绝访问，可能缺少 Cookie/Token 或 User-Agent 被拦截: {response.url}",
            response=response,
        )
    if status == 404:
        raise HTTPError(
            f"404 Not Found — 资源不存在，请检查 URL 或 params 是否正确: {response.url}",
            response=response,
        )

    # 其他 4xx/5xx 统一由 raise_for_status 抛出
    response.raise_for_status()


def demo_pubmed_search(term: str = "diabetes mellitus") -> None:
    """PubMed 搜索示例：params 拼接 + 超时/HTTP 异常处理。"""
    params = {
        "term": term,
        "filter": "datesearch.y_5",  # 近 5 年
        "size": 20,
    }

    try:
        response = fetch_with_params(
            PUBMED_SEARCH_URL,
            params=params,
            timeout=15,
        )
        handle_http_status(response)

        html = response.text
        logger.info("请求成功，HTTP %s，响应体长度 %d 字符", response.status_code, len(html))

        # requests 只能拿到初始 HTML，无法执行页面内的 JavaScript
        if "results-amount" not in html and "search-results" not in html:
            logger.warning(
                "HTML 中缺少文献列表 DOM — 这是动态网页的典型特征，"
                "完整数据需 Playwright 渲染或调用 E-utilities API"
            )

    except Timeout:
        logger.error("请求超时（timeout=%ss），请检查网络或增大 timeout", 15)
    except HTTPError as exc:
        logger.error("HTTP 异常: %s", exc)
    except RequestException as exc:
        logger.error("网络请求失败: %s", exc)


def demo_params_encoding() -> None:
    """演示 params 自动 URL 编码与拼接（httpbin 回显）。"""
    params = {
        "key1": "value1",
        "key2": ["value2", "value3"],  # 同 key 多值 → key2=v2&key2=v3
        "query": "machine learning",
    }

    try:
        response = fetch_with_params(HTTPBIN_GET_URL, params=params, timeout=10)
        handle_http_status(response)
        echoed_args = response.json().get("args", {})
        logger.info("服务器收到的 params: %s", echoed_args)
    except RequestException as exc:
        logger.error("httpbin 演示失败: %s", exc)


def demo_status_error_handling() -> None:
    """演示 403 / 404 异常捕获（httpbin 模拟）。"""
    cases = [
        ("404 示例", "https://httpbin.org/status/404"),
        ("403 示例", "https://httpbin.org/status/403"),
    ]
    for label, url in cases:
        try:
            response = requests.get(url, headers=DEFAULT_HEADERS, timeout=5)
            handle_http_status(response)
        except HTTPError as exc:
            logger.error("[%s] 捕获 HTTPError: %s", label, exc)
        except RequestException as exc:
            logger.error("[%s] 其他异常: %s", label, exc)


# ---------------------------------------------------------------------------
# BeautifulSoup4: find / find_all / select
# ---------------------------------------------------------------------------
#
# 【定位器选择思路】
#   1. 先看页面结构：列表容器 → 单项 → 目标字段（标题/链接/日期）
#   2. 优先用稳定特征：id > 唯一 class > 语义标签 > 属性组合
#   3. 单条结果用 find()，批量用 find_all()，复杂层级用 select()
#   4. 属性读取用 tag.get("attr") 或 tag["attr"]（BS4 无 get_attribute，那是 Playwright）
#
# 【find() vs find_all()】
#   find()      → 返回第一个匹配的 Tag，找不到返回 None
#   find_all()  → 返回 ResultSet（列表），找不到返回 []
#
# 【class 与属性】
#   class 是 Python 保留字，BS4 用 class_="article-item" 传参
#   tag.get("href")     安全读取，缺失返回 None
#   tag.get("href", "") 可设默认值
#   tag["href"]         缺失时抛 KeyError
#   tag.attrs           完整属性字典
#
# 【select() vs find_all()】见文末对比注释
# ---------------------------------------------------------------------------

# 示例 1：静态文章列表页（数据已在 HTML 中，无需 JS）
SAMPLE_ARTICLE_LIST_HTML = """
<html>
<body>
  <section id="news-list" class="article-container">
    <article class="article-item" data-id="101">
      <h2 class="title"><a href="/articles/ai-medicine.html">AI in Medicine</a></h2>
      <span class="date">2024-01-15</span>
    </article>
    <article class="article-item" data-id="102">
      <h2 class="title"><a href="https://example.com/covid-review">COVID-19 Review</a></h2>
      <span class="date">2024-03-20</span>
    </article>
    <article class="article-item featured" data-id="103">
      <h2 class="title"><a href="/articles/diabetes.html">Diabetes Guidelines</a></h2>
      <span class="date">2024-06-01</span>
    </article>
  </section>
</body>
</html>
"""

# 示例 2：多标签嵌套（科室 → 医生 → 专长）
SAMPLE_NESTED_HTML = """
<html>
<body>
  <div class="hospital">
    <div class="department" data-dept="cardiology">
      <h3>Cardiology</h3>
      <ul class="doctors">
        <li class="doctor" data-id="d1">
          <span class="name">Dr. Zhang</span>
          <span class="specialty">Interventional</span>
        </li>
        <li class="doctor" data-id="d2">
          <span class="name">Dr. Li</span>
          <span class="specialty">Electrophysiology</span>
        </li>
      </ul>
    </div>
    <div class="department" data-dept="neurology">
      <h3>Neurology</h3>
      <ul class="doctors">
        <li class="doctor" data-id="d3">
          <span class="name">Dr. Wang</span>
          <span class="specialty">Stroke</span>
        </li>
      </ul>
    </div>
  </div>
</body>
</html>
"""


def parse_html(html: str, parser: str = "html.parser") -> BeautifulSoup:
    return BeautifulSoup(html, parser)


def get_attr(tag: Tag | None, name: str, default: str = "") -> str:
    """读取标签属性（BS4 等价于 Playwright 的 get_attribute）。"""
    if tag is None:
        return default
    return tag.get(name, default) or default


def demo_article_list_extraction(base_url: str = "https://med-news.example.com") -> None:
    """
    示例 1：静态网页文章列表 — 提取标题与链接。

    定位思路：section#news-list → article.article-item → h2.title a
    """
    soup = parse_html(SAMPLE_ARTICLE_LIST_HTML)

    # find()：定位唯一容器
    container = soup.find("section", id="news-list")
    if not container:
        logger.warning("未找到文章列表容器")
        return

    # find_all()：批量获取所有文章项
    articles = container.find_all("article", class_="article-item")
    logger.info("共找到 %d 篇文章", len(articles))

    for article in articles:
        article_id = get_attr(article, "data-id")
        link_tag = article.find("h2", class_="title")
        if link_tag:
            link_tag = link_tag.find("a")

        title = link_tag.get_text(strip=True) if link_tag else ""
        href = get_attr(link_tag, "href")
        full_url = urljoin(base_url, href)
        date_tag = article.find("span", class_="date")
        pub_date = date_tag.get_text(strip=True) if date_tag else ""

        logger.info("[%s] %s | %s | %s", article_id, title, full_url, pub_date)


def demo_nested_traversal() -> None:
    """
    示例 2：多标签嵌套遍历 — 科室 → 医生 → 姓名/专长。

    外层 find_all 科室，内层 find_all 医生，逐层向下钻取。
    """
    soup = parse_html(SAMPLE_NESTED_HTML)

    hospital = soup.find("div", class_="hospital")
    if not hospital:
        logger.warning("未找到 hospital 容器")
        return

    for dept in hospital.find_all("div", class_="department", recursive=False):
        dept_code = get_attr(dept, "data-dept")
        dept_title_tag = dept.find("h3")
        dept_name = dept_title_tag.get_text(strip=True) if dept_title_tag else dept_code

        doctors_ul = dept.find("ul", class_="doctors")
        if not doctors_ul:
            continue

        for doctor in doctors_ul.find_all("li", class_="doctor"):
            doctor_id = get_attr(doctor, "data-id")
            name = doctor.find("span", class_="name")
            specialty = doctor.find("span", class_="specialty")

            logger.info(
                "科室=%s(%s) | 医生=%s(id=%s) | 专长=%s",
                dept_name,
                dept_code,
                name.get_text(strip=True) if name else "",
                doctor_id,
                specialty.get_text(strip=True) if specialty else "",
            )


def demo_select_vs_find_all() -> None:
    """对比 select() 与 find_all() 的写法与适用场景。"""
    soup = parse_html(SAMPLE_ARTICLE_LIST_HTML)

    # find_all：Python 风格，按标签名 + kwargs 过滤
    by_find_all = soup.find_all("article", class_="article-item")
    logger.info("find_all 命中 %d 篇", len(by_find_all))

    # select：CSS 选择器，适合复杂组合条件
    by_select = soup.select("section#news-list article.article-item")
    logger.info("select 命中 %d 篇", len(by_select))

    # 多 class 组合：select 更简洁（find_all 对多 class 需额外处理）
    featured = soup.select("article.article-item.featured")
    logger.info("精选文章(select): %s", featured[0].find("a").get_text(strip=True) if featured else "无")

    # 属性选择器：select 原生支持
    with_data_id = soup.select('article[data-id="102"]')
    if with_data_id:
        logger.info("data-id=102 标题: %s", with_data_id[0].find("a").get_text(strip=True))

    # find() 取单条：等价于 select_one
    first = soup.select_one("article.article-item h2.title a")
    if first:
        logger.info("select_one 首条: %s → %s", first.get_text(strip=True), first.get("href"))


# select() vs find_all() 适用场景
# ┌────────────────────┬──────────────────────────┬────────────────────────────┐
# │                    │ find_all() / find()      │ select() / select_one()    │
# ├────────────────────┼──────────────────────────┼────────────────────────────┤
# │ 语法               │ Python kwargs            │ CSS 选择器字符串           │
# │ 简单标签+class     │ ✅ 直观                  │ ✅ 同样简洁                │
# │ 多 class 同时匹配  │ 需 class_=re 或函数    │ ✅ p.item.featured 一行搞定 │
# │ 父子/兄弟关系      │ find + recursive 参数    │ ✅ div > ul li 层级清晰     │
# │ 属性前缀/后缀      │ 需 re.compile            │ ✅ a[href^="https"]        │
# │ 返回单条           │ find()                   │ select_one()               │
# │ 性能（大文档）     │ 略快                     │ 略慢（Soup Sieve 解析）    │
# │ 推荐场景           │ 逻辑简单、需 Python 过滤 │ 结构复杂、熟悉 CSS 时      │
# └────────────────────┴──────────────────────────┴────────────────────────────┘


# ---------------------------------------------------------------------------
# 静态网页 vs 动态网页（PubMed 为何 requests 拿不到完整文献）
# ---------------------------------------------------------------------------
#
# 【静态网页】
#   服务器直接返回完整 HTML，文献标题/摘要等已在源码中。
#   requests.get → response.text → BeautifulSoup 即可解析。
#   例：部分政府公告页、简单博客、Wikipedia 词条正文。
#
# 【动态网页】
#   首屏 HTML 只是"壳"，真实内容由浏览器执行 JavaScript 后
#   通过 XHR/Fetch 异步请求 API，再动态插入 DOM。
#   requests 不执行 JS，只能拿到空壳 HTML。
#
# 【PubMed 具体情况】
#   https://pubmed.ncbi.nlm.nih.gov/ 搜索结果是动态渲染的：
#   1. 初始 HTML 不含完整文献列表（PMID、标题、作者、摘要等）
#   2. 浏览器加载 JS 后调用 NCBI 内部 API（如 /api/search/...）才填充数据
#   3. 部分字段还有懒加载、分页、展开摘要等交互
#
# 【爬虫方案对比】
#   requests + BeautifulSoup  →  仅适合静态页或公开 REST API
#   Playwright / Selenium       →  模拟浏览器，等 JS 渲染后再取 DOM
#   NCBI E-utilities API        →  PubMed 官方推荐，稳定且合法
#       esearch.fcgi  搜索 PMID
#       efetch.fcgi   拉取摘要/元数据
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    logger.info("=== 1. params 拼接演示 ===")
    demo_params_encoding()

    logger.info("=== 2. 403/404 异常处理演示 ===")
    demo_status_error_handling()

    logger.info("=== 3. PubMed 搜索（requests 局限性演示）===")
    demo_pubmed_search()

    logger.info("=== 4. BS4 文章列表提取（静态页）===")
    demo_article_list_extraction()

    logger.info("=== 5. BS4 多标签嵌套遍历 ===")
    demo_nested_traversal()

    logger.info("=== 6. select() vs find_all() 对比 ===")
    demo_select_vs_find_all()
