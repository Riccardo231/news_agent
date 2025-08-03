#!/usr/bin/env python

import requests
from xml.etree import ElementTree as ET
import re

def fetch_articles(feed_url, user_agent="Mozilla/5.0"):
    res = requests.get(feed_url, timeout=10, headers={"User-Agent": user_agent})
    res.raise_for_status()
    root = ET.fromstring(res.text)
    articles = []
    for item in root.findall('.//item'):
        title = item.findtext('title', '')
        link = item.findtext('link', '')
        pubDate = item.findtext('pubDate', '')
        description = item.findtext('description', '')
        source_el = item.find('source')
        author = source_el.text if source_el is not None else ""
        clean_descr = re.sub('<[^<]+?>', '', description)
        articles.append({
            "title": title.strip(),
            "date": pubDate.strip(),
            "author": author.strip(),
            "summary": clean_descr.strip(),
            "link": link.strip(),
        })
    return articles
