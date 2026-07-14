import asyncio
import csv
import logging
import random
import urllib.parse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential, before_log

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
]

URL = "https://pubmed.ncbi.nlm.nih.gov/?term=antibody+drug&sort=date"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

@retry(
    retry=retry_if_exception_type((PlaywrightTimeoutError, Exception)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    before=before_log(logging.getLogger(__name__), logging.INFO),
)
async def goto_with_retry(page, url: str):
    logging.info("开始打开页面：%s", url)
    response = await page.goto(url, wait_until="networkidle", timeout=30000)
    if response:
        logging.info("页面响应状态：%s", response.status)
    return response

async def extract_pubmed_results(page, max_items=10):
    await page.wait_for_selector("article.full-docsum", timeout=30000)

    articles = page.locator("article.full-docsum")
    total = min(await articles.count(), max_items)

    results = []
    for index in range(total):
        item = articles.nth(index)

        title = await item.locator("a.docsum-title").inner_text()
        href = await item.locator("a.docsum-title").get_attribute("href")
        link = urllib.parse.urljoin("https://pubmed.ncbi.nlm.nih.gov", href or "")

        pmid = await item.locator("span.docsum-pmid").inner_text()
        authors_locator = item.locator("span.docsum-authors.full-authors").first
        # 判断第一种选择器有没有元素
        if await authors_locator.count() == 0:
            # 找不到就降级，只匹配 span.docsum-authors（只保留基础class，忽略full-authors）
            authors_locator = item.locator("span.docsum-authors").first
        # 最后读取文本
        authors = await authors_locator.inner_text()


        results.append({
            "标题": title.strip(),
            "作者": authors.strip(),
            "PMID": pmid.strip(),
            "链接": link,
        })

    return results
 

async def extract_abstract_from_detail(page, link, max_attempts=3):
    """
    在详情页抓取摘要的更稳健实现：
    - 增大等待超时并做多次尝试（内部重试 + 前后滚动等待）
    - 尝试点击可能存在的“Show more / more / full”按钮展开全文
    - 若多次尝试失败，返回空字符串而不是抛出异常
    """
    backoff_base = 1
    for attempt in range(1, max_attempts + 1):
        try:
            await page.goto(link, wait_until="domcontentloaded", timeout=40000)
            # 首先等待可能的摘要容器出现
            await page.wait_for_selector("div.abstract-content, div.abstr, div#abstract", timeout=20000)

            # 尝试展开“更多/Show more”类按钮（常见的展开形式）
            expand_selectors = [
                'button:has-text("Show more")',
                'button:has-text("Show full")',
                'a:has-text("Show more")',
                'button.more-link',
                'button.inline-show-more',
                'button:has-text("More")',
            ]
            for sel in expand_selectors:
                loc = page.locator(sel)
                if await loc.count() > 0:
                    try:
                        await loc.first.click(timeout=3000)
                        await page.wait_for_timeout(300)  # 等待展开动画
                    except Exception:
                        pass  # 点击失败忽略，继续尝试其它选择器

            # 最终定位摘要容器并读取文本
            locator = page.locator("div.abstract-content.selected, div.abstract-content, div.abstr, div#abstract").first
            if await locator.count() == 0:
                # 如果未找到，再滚动并短暂等待后重试循环
                await page.evaluate("window.scrollBy(0, window.innerHeight);")
                await asyncio.sleep(backoff_base * attempt)
                continue

            text = (await locator.inner_text(timeout=5000)).strip()
            if text:
                return text
            # 若取得为空，短暂等待并重试
            await asyncio.sleep(backoff_base * attempt)
        except PlaywrightTimeoutError:
            # 加强等待后重试
            await asyncio.sleep(backoff_base * attempt)
        except Exception:
            # 其他异常也做短暂等待然后重试
            await asyncio.sleep(backoff_base * attempt)

    # 所有尝试失败，返回空字符串（调用方可记录警告）
    return ""

async def enrich_with_abstract(context, rows):
    """
    为每条结果打开详情页抓取摘要，使用单独的 detail_page 避免影响主页面定位。
    若摘要为空或抓取超时，保留空字符串并记录警告，继续处理其余条目。
    """
    detail_page = await context.new_page()
    for row in rows:
        try:
            abstract = await extract_abstract_from_detail(detail_page, row["链接"], max_attempts=4)
            if not abstract:
                logging.warning("摘要为空或未获取到（PMID=%s）: %s", row.get("PMID", ""), row.get("链接", ""))
            row["摘要"] = abstract
            logging.info("已抓取摘要：%s", row.get("PMID", ""))
            # 小休眠，减缓请求速率，降低触发反爬风险
            await detail_page.wait_for_timeout(300 + random.randint(100, 600))
        except PlaywrightTimeoutError:
            logging.warning("详情页摘要加载超时：%s", row.get("链接", ""))
            row["摘要"] = ""
        except Exception as exc:
            logging.warning("详情页摘要抓取失败：%s %s", row.get("链接", ""), exc)
            row["摘要"] = ""
    await detail_page.close()
    return rows

def save_to_csv(rows, filepath="antibody_drug.csv"):
    header = ["标题", "作者", "PMID", "链接", "摘要"]
    with open(filepath, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    logging.info("已导出到文件：%s", filepath)

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        user_agent = random.choice(USER_AGENTS)
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()

        logging.info("使用随机 User-Agent：%s", user_agent)

        try:
            await goto_with_retry(page, URL)
            await page.wait_for_load_state("networkidle", timeout=30000)
            logging.info("页面加载完成")

            rows = await extract_pubmed_results(page, max_items=10)
            rows = await enrich_with_abstract(context, rows)
            if rows:
                save_to_csv(rows)
            else:
                logging.warning("未找到任何结果。")
        except PlaywrightTimeoutError as exc:
            logging.error("页面加载超时：%s", exc)
        except Exception as exc:
            logging.error("抓取过程中发生错误：%s", exc)
        finally:
            await browser.close()
            logging.info("浏览器已关闭")

if __name__ == "__main__":
    asyncio.run(main())