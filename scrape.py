import lxml.html
import pandas as pd

BASE_URL = 'http://bid.ma/'


def extract_price(price_str):
    return float(price_str.split(' ')[0].replace(',', ''))


def scrape_finished_auction(url=None, content=None):
    if content:
        page = lxml.html.fromstring(content)
    elif url:
        page = lxml.html.parse(url)
    else:
        raise ValueError("Must pass a url the content of an HTML page")

    root = page.xpath('//ul[@id="winnersList"]')[0]
    product_names = [e.text for e in root.xpath('.//h2[@class="productName"]/a')]
    product_links = [BASE_URL + e.attrib['href'] for e in root.xpath('.//h2[@class="productName"]/a')]
    product_prices = [extract_price(e.text) for e in root.xpath('.//div[@class="productPrice"]') if e.text]
    product_values = [extract_price(e.text) for e in root.xpath('.//div[@class="productValue"]/strong') if e.text]
    product_owners = [' '.join(e.text.split(',')[0].split(' ')[2:]) for e in root.xpath('.//strong[@class="author"]') if e.text]
    product_date = [e.text.split(' ')[-1] for e in root.xpath('.//strong[@class="author"]') if e.text]

    df = pd.DataFrame(dict(name=product_names, link=product_links, price=product_prices, value=product_values,
                           owner=product_owners, date=product_date))
    return df

if __name__ == '__main__':
    MAX_PAGE = 135

    dfs = []
    print("* Scraping product pages from bid.ma, up to the page #{}".format(MAX_PAGE))
    for i in range(1, MAX_PAGE + 1):
        url = "http://bid.ma/allauctions.php?aid=3&pgno={}".format(i)
        print("  . Scraping page {}/{}...".format(i, MAX_PAGE))
        products_df = scrape_finished_auction(url=url)
        dfs.append(products_df)

    df = pd.concat(dfs)
    df.to_csv('bid_ma.csv', index=False)
