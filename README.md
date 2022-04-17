# Coding challenge from ReviewTrackers


Function api.get_reviews(url, crawl=False, sort_by_oldest=False, retry_on_rate_limit=False, page_limit=0)

Parameters:
    str url: base URL to process (e.g. https://www.productreview.com.au/listings/expert-electrical)
    bool crawl: when True, will try to explore multiple pages within specified base URL
    bool sort_by_oldest: when True, request oldest-to-newest ordering of reviews before paginating
    bool retry_on_rate_limit: when True, wait and retry request if encountered HTTP status code 429
    int page_limit: when >= 0, limit number of requested pages per each star rating to this number

Returns:
    dict {"http_response": str, "job_status": str, "data": dict}
