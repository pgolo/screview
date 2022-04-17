# Coding challenge from ReviewTrackers

## Function api.get_reviews()

### Parameters:

- str url: URL to request page from  
- bool crawl: when True, will try to explore multiple pages within specified base URL
- bool sort_by_oldest: when True, request oldest-to-newest ordering of reviews before paginating
- bool retry_on_rate_limit: when True, wait and retry request if encountered HTTP status code 429
- int page_limit: when >= 0, limit number of requested pages per each star rating to this number

### Returns:

- dict {"http_response": str, "job_status": str, "data": dict}
