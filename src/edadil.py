import asyncio

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import src.config as config

BASE_URL = 'https://edadeal.ru'
URL = 'https://edadeal.ru/novosibirsk'

LOAD_DELAY = 5
SEGMENTS_LIMIT = 6


class Edadil:
    async def update(self):
        config.EDADIL_SEGMENTS = await self.get_segments()

        if SEGMENTS_LIMIT is not None:
            config.EDADIL_SEGMENTS = config.EDADIL_SEGMENTS[:SEGMENTS_LIMIT]

        # Load segments items
        for segment in config.EDADIL_SEGMENTS:
            config.EDADIL_SEGMENTS_ITEMS.append(
                await self.get_items(segment['link']))

        return True

    async def get_segments(self):
        options = Options()
        options.headless = True

        browser = webdriver.Firefox(options=options)

        browser.get(URL)

        # Wait for the page to load
        await asyncio.sleep(LOAD_DELAY)

        soup = bs(browser.page_source, features="html.parser")
        browser.close()

        segments = soup.find_all(
            'a', class_='p-index__segment p-index__segment_last_false')
        segments.extend(soup.find_all(
            'a', class_='p-index__segment p-index__segment_last_true'))

        r_segments = []

        for segment in segments:
            r_segments.append({
                'name': segment.find('div', class_='p-index__segment-title').text.replace('\xa0', ' '),
                'link': BASE_URL + segment.get('href') + '&sort=ddiscount'})

        return r_segments

    async def get_items(self, url: str):
        options = Options()
        options.headless = True

        browser = webdriver.Firefox(options=options)

        browser.get(url)

        # Wait for the page to load
        await asyncio.sleep(LOAD_DELAY)

        soup = bs(browser.page_source, features="html.parser")
        browser.close()

        items = soup.find_all('div', class_='b-offer__root')
        r_item = []

        for item in items:
            item_desc = item.find('div', class_='b-offer__description')
            item_name = item_desc.get('title') or item_desc.text

            if not item_name:
                continue

            offer_info = item.find('div', class_='b-offer__offer-info')

            if not offer_info:
                continue

            item_shop_frame = offer_info.find('img', class_='b-image__img')

            if not item_shop_frame:
                continue

            item_shop = item_shop_frame.get('alt')

            if not item_shop:
                continue

            price_new = float(item.find('div', 'b-offer__price-new').text.replace(
                'От', '').replace(' ₽', '').replace(',', '.').replace('\xa0', ''))
            price_old = float(item.find('div', 'b-offer__price-old').text.replace(
                'От', '').replace(' ₽', '').replace(',', '.').replace('\xa0', ''))

            if not price_new or not price_old:
                continue

            sale_perc = round((1 - price_new / price_old) * 100, 1)

            r_item.append({
                'name': item_name.replace('\xa0', ' '),
                'shop': item_shop.replace('\xa0', ' '),
                'price': price_new,
                'old_price': price_old,
                'sale_perc': sale_perc
            })

        r_item.sort(key=lambda item: item['sale_perc'], reverse=True)

        return r_item

    async def get_search_items(self, search_text: str):
        return await self.get_items(f'{URL}/offers?q={search_text}&sort=ddiscount')
