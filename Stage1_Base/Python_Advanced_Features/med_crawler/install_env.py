#!/usr/bin/env python3
"""一键安装爬虫全套依赖。"""

import logging
import subprocess
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)

# bs4 对应 PyPI 包 beautifulsoup4；logging 为 Python 标准库，无需 pip 安装
PACKAGES = [
    "requests",
    "beautifulsoup4",
    "playwright",
    "pandas",
    "tenacity",
]


def run(cmd: list[str], desc: str) -> bool:
    logging.info("开始: %s", desc)
    try:
        subprocess.run(cmd, check=True)
        logging.info("成功: %s", desc)
        return True
    except subprocess.CalledProcessError as exc:
        logging.error("失败: %s (exit code %s)", desc, exc.returncode)
        return False


def main() -> int:
    logging.info("=" * 50)
    logging.info("爬虫环境一键安装")
    logging.info("=" * 50)

    pip_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", *PACKAGES]
    if not run(pip_cmd, f"安装依赖: {', '.join(PACKAGES)}"):
        return 1

    playwright_cmd = [sys.executable, "-m", "playwright", "install", "chromium"]
    if not run(playwright_cmd, "安装 Playwright Chromium 浏览器"):
        return 1

    logging.info("=" * 50)
    logging.info("全部安装完成！")
    logging.info("  requests / bs4 / playwright / pandas / tenacity 已就绪")
    logging.info("  Playwright Chromium 已安装")
    logging.info("  logging 为 Python 标准库，无需单独安装")
    logging.info("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(main())
