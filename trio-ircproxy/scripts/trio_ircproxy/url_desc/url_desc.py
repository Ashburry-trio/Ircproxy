#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import annotations

#import http3
import requests
flood = 0

def get_desc(url,/, *, flood=flood):
    flood += 1
    #client = http3.AsyncClient()
    #page = client.get('url')
    page = requests.get(url)
    page_text: str = page.text
    while '\n' in page_text:
        page_text = page_text.replace('\n','')
    while '  ' in page_text:
        page_text = page_text.replace('  ', ' ')
    page_text_low = page_text.lower()
    # while chr(39) in page_text_low:
    #    page_text_low = page_text_low.replace(chr(39), '"')
    tit_start = page_text_low.find('<title')
    if tit_start == -1:
        print('NO TITLE')
        return
    find_close = page_text[tit_start:]
    find_close_1 = find_close
    find_close_int = find_close.find('>')
    ans = find_close_1[find_close_int + 1:][:find_close_1[find_close_int:].find('<') - 1]
    print(f'Title: {ans[:70]}')

    desc = page_text_low.find('<meta name="description" content="')
    desc = page_text[desc+34:]
    desc_end = desc.find('/>') - 2
    desc = desc[:desc_end]
    print(f'Description: {desc}')
    flood -= 1
get_desc('https://www.mslscript.com')