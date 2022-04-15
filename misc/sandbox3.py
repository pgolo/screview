import cloudscraper

scraper = cloudscraper.CloudScraper()
url = 'https://www.productreview.com.au/listings/hotondo-homes?page=10'
response = scraper.get(url)
content = response.text
print(content[:1000])
