#!/usr/bin/env python3
"""Data Spider - 通用数据采集工具"""

import logging
import random
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("spider.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# User-Agent 池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
]

# 代理池（示例，需替换为真实代理）
PROXY_POOL = [
    # "http://proxy1:8080",
    # "http://proxy2:8080",
]


class DataSpider:
    def __init__(self):
        self.session = requests.Session()
        self.results = []

    def get_headers(self):
        return {"User-Agent": random.choice(USER_AGENTS)}

    def get_proxy(self):
        if PROXY_POOL:
            proxy = random.choice(PROXY_POOL)
            return {"http": proxy, "https": proxy}
        return None

    def fetch(self, url: str) -> str:
        """抓取单个页面"""
        try:
            resp = self.session.get(
                url, headers=self.get_headers(), proxies=self.get_proxy(), timeout=10
            )
            resp.raise_for_status()
            logger.info(f"成功抓取: {url}")
            return resp.text
        except Exception as e:
            logger.error(f"抓取失败 {url}: {e}")
            return ""

    def parse(self, html: str, selectors: dict) -> dict:
        """解析页面数据"""
        soup = BeautifulSoup(html, "lxml")
        result = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            result[key] = [el.get_text(strip=True) for el in elements]
        return result

    def run_task(self, targets: list):
        """执行采集任务"""
        for target in targets:
            html = self.fetch(target["url"])
            if html:
                data = self.parse(html, target.get("selectors", {}))
                self.results.append({"url": target["url"], "data": data, "time": datetime.now().isoformat()})
                logger.info(f"解析完成: {target['url']} -> {len(data)} fields")

    def save_results(self, filename: str = "results.json"):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        logger.info(f"结果已保存: {filename}")


def scheduled_job():
    logger.info("=== 定时任务执行 ===")
    spider = DataSpider()
    # 示例目标（需替换为真实目标）
    targets = [
        {"url": "https://example.com", "selectors": {"title": "h1", "content": "p"}},
    ]
    spider.run_task(targets)
    spider.save_results()


if __name__ == "__main__":
    logger.info("Data Spider 启动")

    # 立即执行一次
    scheduled_job()

    # 定时任务（每天 9:00 执行）
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduled_job, "cron", hour=9, minute=0)
    logger.info("定时任务已设置: 每天 09:00 执行")
    scheduler.start()
