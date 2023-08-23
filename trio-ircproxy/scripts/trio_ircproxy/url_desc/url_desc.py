#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

import http3
#import requests


async def get_url_desc(url):
    client = http3.AsyncClient()
    page = await client.get(url)
    # page = requests.get(url)
    page_text: str = page.text
    while '\n' in page_text:
        page_text = page_text.replace('\n', '')
    while '  ' in page_text:
        page_text = page_text.replace('  ', ' ')
    page_text_low = page_text.lower()
    # while chr(39) in page_text_low:
    #    page_text_low = page_text_low.replace(chr(39), '"')
    tit_start = page_text_low.find('<title')
    if tit_start > -1:
        find_close = page_text[tit_start:]
        find_close_1 = find_close
        find_close_int = find_close.find('>')
        ans = find_close_1[find_close_int + 1:][:find_close_1[find_close_int:].find('<') - 1]
        if not ans:
            ans = 'nothing to show.'
    else:
        ans = 'nothing to show.'
    ans = ans[:70]
    desc = page_text_low.find('<meta name="description" content="')
    desc = page_text[desc+34:]
    desc_end = desc.find('/>') - 2
    desc = desc[:desc_end]
    if not desc:
        desc = 'nothing to show.'
    desc = desc[:160]

    title = ans
    tit_desc = (url, title, desc)
    return tit_desc

class URLFloodError(Exception):
    pass
