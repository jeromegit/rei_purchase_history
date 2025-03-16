import json
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Union, Optional

import browser_cookie3
import requests
from tabulate import tabulate
from bs4 import BeautifulSoup


# IMPORTANT FIRST STEP BEFORE RUNNING ANY OF THIS...
# Manually login to rei.com using Chrome

def convert_date_format(date_string):
    try:
        # Parse the date string
        date_obj = datetime.strptime(date_string, "%A, %b %d, %Y")

        # Format it to YYYY-MM-DD
        formatted_date = date_obj.strftime("%Y-%m-%d")

        return formatted_date

    except ValueError as e:
        return f"Error parsing date: {e}"


def get_rei_session():
    site = 'rei.com'
    cookie_jar = browser_cookie3.chrome(domain_name=site)
    cookies = {cookie.name: cookie.value for cookie in cookie_jar}

    session = requests.Session()
    session.cookies.update(cookies)

    # these should be extracted using the DevTools > Network
    # then use "Copy as fetch" for most
    # "Copy as cURL" for the user-agent value
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "en-US,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,es;q=0.6",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    }

    session.headers.update(headers)

    return session


def get_json_data_for_url(session, url):
    response = session.get(url)
    json_str = response.text
    json_data = json.loads(json_str)

    return json_data


def get_online_purchase_items_in_order(session, purchase_order_id):
    # https://www.rei.com/order-details/rs/purchase-details/A319493263
    purchase_items_url = f'https://www.rei.com/order-details/rs/purchase-details/{purchase_order_id}'
    json_data = get_json_data_for_url(session, purchase_items_url)
    fulfillment_items = [group["fulfillmentItems"] for group in json_data["fulfillmentGroups"]]
    order_date = json_data["orderDate"][:10]
    purchase_items = []
    for items in fulfillment_items:
        for item in items:
            purchase_item = {k: item[k] for k in {'sku', 'name', 'brand', 'price'}}
            purchase_item['order_date'] = order_date
            purchase_items.append(purchase_item)

    return purchase_items


def print_purchase_items(purchase_items):
    headers = ["order_date", "brand", "name", "sku", "price"]
    table_data = [[item.get(key, "") for key in headers] for item in purchase_items]
    print(tabulate(table_data, headers=headers, tablefmt="psql"))


def get_online_purchases_for_year(session, year):
    online_purchases_for_year_url = f"https://www.rei.com/order-details/rs/purchase-details/history?year={year}"
    json_data = get_json_data_for_url(session, online_purchases_for_year_url)
    if "history" in json_data:
        purchase_order_ids = [order["orderId"] for order in json_data["history"]]

        for purchase_order_id in purchase_order_ids:
            purchase_items = get_online_purchase_items_in_order(session, purchase_order_id)
            print_purchase_items(purchase_items)


def get_single_purchase_item(soup, html):
    sku = html.find('li', {'data-ui': 'product-sku'})
    if sku:
        sku_text = sku.text.strip()
        sku = sku_text.replace('Item #', '').strip()
        name = soup.select_one('[data-ui="product-title"] a').text.strip()
        price = soup.select_one('[data-ui="product-total-price"]').text.strip()
        order_date = soup.select_one('[data-ui="order-date"]').text.strip()
    else:
        sku = name = 'n/a'
        price = soup.select_one('[data-ui="total-value"]').text
        order_date = html.find('li', {'data-ui': 'order-date'})

    price = price.replace('$', '')
    brand = 'n/a'
    order_date = convert_date_format(order_date)
    purchase_item = {'sku': sku, 'name': name, 'brand': brand, 'price': price, 'order-date': order_date}

    return purchase_item


def get_instore_purchase_items_in_order(session, purchase_order_id):
    purchase_item_url = f"https://www.rei.com/retail-purchase-details?from_url=PurchaseHistoryView&fromSubmit=true&orderId={purchase_order_id}&retailPurchase=true"
    response = session.get(purchase_item_url)
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')
    purchase_items = []
    product_sections = soup.find_all('div', class_='product-section')
    if product_sections:
        for section in product_sections:
            purchase_item = get_single_purchase_item(soup, section)
            purchase_items.append(purchase_item)
    else:
        purchase_item = get_single_purchase_item(soup, html)
        purchase_items.append(purchase_item)

    return purchase_items


def get_instore_purchases_for_year(session, year):
    purchase_items_url = f"https://www.rei.com/rest/user/orders?year={year}&includeSkus=true&retailOnly=true"
    json_data = get_json_data_for_url(session, purchase_items_url)
    purchase_order_ids = [order["csaOrderId"] for order in json_data]
    print(f"{year} {purchase_order_ids}")

    for purchase_order_id in purchase_order_ids:
        purchase_items = get_instore_purchase_items_in_order(session, purchase_order_id)
    print_purchase_items(purchase_items)


def get_all_online_purchases(session, years):
    for year in years:
        get_online_purchases_for_year(session, year)


def get_all_instore_purchases(session, years):
    for year in years:
        get_instore_purchases_for_year(session, year)


if __name__ == "__main__":
    session = get_rei_session()

    years = list(range(2016, 2025))
    # years = list(range(2024, 2025))
    # get_all_online_purchases(session, years)
    get_all_instore_purchases(session, years)
