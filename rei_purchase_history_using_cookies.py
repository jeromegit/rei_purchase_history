import browser_cookie3
import requests

site = 'rei.com'
cookie_jar = browser_cookie3.chrome(domain_name=site)
cookies = {cookie.name: cookie.value for cookie in cookie_jar}

session = requests.Session()
session.cookies.update(cookies)

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


purchase_historty_2024_url = 'https://www.rei.com/order-details/rs/purchase-details/history?year=2024'
response = session.get(purchase_historty_2024_url, headers=headers)
print(response.text)
