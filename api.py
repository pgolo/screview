import datetime
import json
import math
import re
import requests
import time
import threading
from bs4 import BeautifulSoup
from flask import Flask, request, logging, abort

app = Flask(__name__)
logger = logging.create_logger(app)
logger.root.setLevel('INFO')

# (for the sake of an example) local kv-storage for asynk tasks
JOBS = {}


def try_challenge(initial_response):
    """Handle Cloudflare challenge"""
    # not implemented
    logger.warning('Status code 503, not handled')
    return False, 'Completed, status code %s' % (initial_response.status_code), None


def try_get_request(url, retry_on_rate_limit=True):
    """Send GET request.
    
    Args:
        str url: URL to send request to
        bool retry_on_rate_limit: when True, if rate limit is encountered on the remote, we will wait and retry
    """
    logger.info('Requesting %s' % (url))
    try:
        response = requests.get(url)
    except requests.exceptions.MissingSchema:
        return False, 'Failed, invalid URL', None
    except requests.exceptions.ConnectionError:
        return False, 'Failed, connection error', None
    logger.info('Got response, status code %d' % (response.status_code))
    if response.status_code == 200:
        return True, 'Completed, status code %s' % (response.status_code), response
    elif response.status_code == 503: # challenge?
        return try_challenge(response)
    elif response.status_code == 429: # rate limit?
        retry_after = int(response.headers['retry-after'])
        logger.warning('Rate limit allows retrying in %d seconds' % (retry_after))
        if retry_on_rate_limit:
            logger.info('Retrying in %d s' % (retry_after))
            time.sleep(retry_after)
            return try_get_request(url, retry_on_rate_limit=False)
        logger.warning('Will not retry, moving on')
    return False, 'Completed, status code %s' % (response.status_code), None


def get_rating_distribution(soup):
    """Locate and parse specific section of a page containg review rating distribution.

    Args:
        BeautifulSoup soup: object representing parsed HTML page
    """
    script_child = soup.find(string=re.compile(r'^window.__ssr_data'))
    if script_child is None:
        logger.warning('Could not find section to extract ratingDistribution from')
        return []
    script_element = script_child.parent
    script_text = script_element.text[19:-2].replace('\\\\n', '\n').replace('\\\\', '$backslash').replace('\\', '').replace('$backslash', '\\')
    try:
        script_json = json.loads(script_text, strict=False)
        rating_distribution = script_json['reduxAsyncConnect']['itemsMap']['listingPageAsyncDataContainer']['data']['listing']['statistics']['ratingDistribution']
    except:
        logger.warning('Found relevant section, but could not extract ratingDistribution')
        return []
    logger.info('Extracted ratingDistribution=%s' % (str(rating_distribution)))
    return rating_distribution


def parse_html(html, get_ssr_data, url, response_description):
    """Parse HTML content (supposedly returned as some response.text)

    Args:
        str html: text to parse (expecting HTML page with reviews)
        bool get_ssr_data: when True, specific part of the page containing review rating distribution will be parsed as well
        str url: URL from where HTML was originally retrieved
        str response_description: message from helper function that was sending HTTP request
    """
    total_reviews, rating_distribution, reviews = 0, [], {}
    soup = BeautifulSoup(html, 'html.parser')
    content_element = soup.find(name='script', attrs={'data-react-helmet': 'true'})
    
    if content_element is None: # page is likely invalid
        msg = 'Page is invalid: %s' % (url)
        logger.warning(msg)
        return response_description, msg, total_reviews, rating_distribution, reviews
    
    if get_ssr_data:
        rating_distribution = get_rating_distribution(soup)
    
    content = json.loads(content_element.text)
    if 'aggregateRating' not in content: # page is likely invalid
        msg = 'Page is invalid: %s' % (url)
        logger.warning(msg)
        return response_description, msg, total_reviews, rating_distribution, reviews

    total_reviews = content['aggregateRating']['reviewCount']
    if total_reviews > 0 and 'review' in content:
        for review in content['review']:
            reviews[review['url']] = {'title': review['headline'], 'content': review['reviewBody'], 'author_name': review['author']['name'], 'author_uri': review['author']['sameAs'], 'rating': review['reviewRating']['ratingValue'], 'date': review['datePublished']}
    msg = 'Page %s: reviewCount=%d; extracted from page: %d' % (url, total_reviews, len(reviews))
    logger.info(msg)
    return response_description, msg, total_reviews, rating_distribution, reviews


def get_reviews_from_page(url, retry_on_rate_limit, get_ssr_data=False):
    """Request single page and parse it.
    
    Args:
        str url: URL of the page to parse
        bool retry_on_rate_limit: when True, if rate limit is encountered on the remote, we will wait and retry
        bool get_ssr_data: when True, specific part of the page containing review rating distribution will be parsed as well
    """
    success, response_description, response = try_get_request(url, retry_on_rate_limit)
    if not success:
        msg = 'Failed to load page %s' % (url)
        logger.warning(msg)
        return response_description, msg, 0, [], {}    
    return parse_html(response.text, get_ssr_data, url, response_description)


def page_url(base_url, star_rating, page_number, sort_by_oldest=False):
    """Construct URL using provided parameters.
    
    Args:
        str base_url: URL stripped of any parameters
        int star_rating: review rating
        int page_number: page number
        bool sort_by_oldest: when True, sort reviews 'oldest to newest' first before retrieving a page
    """
    if sort_by_oldest:
        url = '%s?sortBy=oldest&rating=%d' % (base_url, star_rating)
    else:
        url = '%s?rating=%d' % (base_url, star_rating)
    if page_number > 1:
        url = '%s&page=%d' % (url, page_number)
    logger.info('Will request rating=%d, page=%d, ordered %s first (%s)' % (star_rating, page_number, 'oldest' if sort_by_oldest else 'newest', url))
    return url


def get_reviews(url, crawl=False, sort_by_oldest=False, retry_on_rate_limit=False, page_limit=0):
    """Process one or more pages starting with specified URL and return collected reviews.
    
    Args:
        str url: URL to process
        bool crawl: when True and there are more reviews than fit single page, other pages with same base URL will be processed as well
        bool sort_by_oldest: when True, additional pages will be loaded when reviews are sorted 'oldest to newest'
        bool retry_on_rate_limit: when True, if rate limit is encountered on the remote, we will wait and retry
        int page_limit: when >= 0, limit number of requested pages per each star rating to this number
    """
    # get first page and check if we have all the reviews with one shot
    last_response_description, last_msg, total_reviews, rating_distribution, reviews = get_reviews_from_page(url, retry_on_rate_limit, get_ssr_data=True)
    if total_reviews == 0:
        logger.warning('Did not get any reviews from requested page')
        return {'http_response': last_response_description, 'job_status': last_msg, 'data': reviews}
    elif total_reviews == len(reviews) or not crawl:
        logger.info('%s' % ('Got all reviews in one go' if crawl else 'Got reviews from requested page (will not look further)'))
        return {'http_response': last_response_description, 'job_status': last_msg, 'data': reviews}
    logger.info('Reviews take more than 1 page, will try crawling')
    # stratify by star rating, then by page number
    if not rating_distribution:
        rating_distribution = [total_reviews] * 5
    base_url = url.split('?')[0]
    got_reviews = {}
    processed_pages = {}
    for star_rating in range(1, 6):
        if rating_distribution[star_rating-1] == 0:
            continue
        expected_pages_count = math.ceil(rating_distribution[star_rating-1] / 25)
        if star_rating in processed_pages and processed_pages[star_rating] == expected_pages_count:
            logger.info('Already got all pages for rating=%d' % (star_rating))
            continue
        logger.info('Star rating %d: expecting %d page%s' % (star_rating, expected_pages_count, 's' if expected_pages_count != 1 else ''))
        for page_number in range(1, expected_pages_count+1):
            if page_limit > 0 and page_number > page_limit:
                logger.warning('Will not process pages beyond page %d' % page_limit)
                break
            next_url = page_url(base_url, star_rating, page_number, sort_by_oldest)
            try:
                last_response_description, last_msg, _, _, got_reviews = get_reviews_from_page(next_url, retry_on_rate_limit)
                processed_pages[star_rating] = page_number
            except:
                pass
            reviews.update(got_reviews)
            logger.info('Total reviews collected so far: %d (%s)' % (len(reviews), url))
    logger.info('Got %d reviews from %s' % (len(reviews), url))
    return {'http_response': last_response_description, 'job_status': last_msg, 'data': reviews}


def run_job(job_id, method, *args, **kwargs):
    """Wrap get_reviews() function in a job.

    Args:
        str job_id: ID of a job to store
        object method: procedure to execute (expected to return iterable with at least 3 items)
        *args, **kwargs: parameters for method
    """
    global JOBS
    JOBS[job_id] = {'http_response': 'N/A', 'job_status': 'In progress', 'data': {}}
    result = method(*args, **kwargs)
    JOBS[job_id] = result


# Views

@app.route('/', methods=['GET', 'POST'])
def scrape():
    """Get parameters and either parse single page right away and return the results,
    or start job in a separate thread and return endpoint to retrieve the results later.
    """
    global JOBS
    if request.method == 'GET':
        # parse single page
        url = request.args['url']
        result = get_reviews(url=url)
        return result
    elif request.method == 'POST':
        # promise to parse what is requested, and execute in a separate thread
        url = request.args['url']
        crawl = request.args['crawl'].lower() == 'true' if 'crawl' in request.args else False
        sort_oldest_first = request.args['oldest_first'].lower() == 'true' if 'oldest_first' in request.args else False
        retry_on_rate_limit = request.args['retry_on_rate_limit'].lower() == 'true' if 'retry_on_rate_limit' in request.args else False
        page_limit = int(request.args['page_limit']) if 'page_limit' in request.args and request.args['page_limit'].isdigit() else 0
        job_id = str(datetime.datetime.timestamp(datetime.datetime.now()))
        JOBS[job_id] = {'http_response': 'N/A', 'job_status': 'Requested', 'data': {}}
        t = threading.Thread(target=run_job, args=(job_id, get_reviews, url, crawl, sort_oldest_first, retry_on_rate_limit, page_limit))
        t.run()
        return {'fetch_results_at': '/result?job_id=%s' % (str(job_id))}
    abort(400)


@app.route('/jobs', methods=['GET'])
def result():
    """Return list of async jobs"""
    global JOBS
    return {'jobs': list(JOBS.keys())}


@app.route('/result', methods=['GET'])
def jobs():
    """Return result of a job done asynchronously"""
    global JOBS
    job_id = request.args['job_id']
    if job_id in JOBS:
        return JOBS[job_id]
    abort(400)


if __name__ == '__main__':
    app.run(port=5000)
