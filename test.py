import api
import requests
from bs4 import BeautifulSoup
from mock import patch
import unittest

class TestApi(unittest.TestCase):

    def test_try_challenge(self):
        pass

    def test_try_get_request(self):
        with patch('requests.get') as patched_get:
            result = api.try_get_request('some_url', False)
            patched_get.assert_called_with('some_url')
            assert type(result) == tuple
            assert len(result) == 3
            assert type(result[0]) == bool
            assert type(result[1]) == str
            assert type(result[2]) == requests.Response or result[2] is None
    
    def test_try_get_request_connection_error(self):
        result = api.try_get_request('https://missing_location')
        assert result[0] == False
        assert result[1] == 'Failed, connection error'
        assert result[2] is None

    def test_try_get_request_invalid_url(self):
        result = api.try_get_request('invalid_url')
        assert result[0] == False
        assert result[1] == 'Failed, invalid URL'
        assert result[2] is None

    def test_get_rating_distribution_ok_1(self):
        with open('./testdata/reviews_present_1.html', mode='r', encoding='utf8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        expected = [24, 8, 1, 40, 751]
        result = api.get_rating_distribution(soup)
        assert result == expected

    def test_get_rating_distribution_ok_2(self):
        with open('./testdata/reviews_present_2.html', mode='r', encoding='utf8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        expected = [0, 0, 0, 12, 152]
        result = api.get_rating_distribution(soup)
        assert result == expected

    def test_get_rating_distribution_failed(self):
        with open('./testdata/challenge_page.html', mode='r', encoding='utf8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        expected = []
        result = api.get_rating_distribution(soup)
        assert result == expected

    def test_parse_html_1(self):
        with open('./testdata/reviews_present_1.html', mode='r', encoding='utf8') as f:
            html = f.read()
        result = api.parse_html(html, True, 'test_url', 'Completed, status code 200')
        assert type(result) == tuple
        assert len(result) == 5
        assert result[0] == 'Completed, status code 200'
        assert result[1] == 'Page test_url: reviewCount=824; extracted from page: 25'
        assert result[2] == 824
        assert result[3] == [24, 8, 1, 40, 751]
        assert type(result[4]) == dict
        assert 'https://www.productreview.com.au/reviews/4d0efe70-272a-5933-a2c3-d8a8794dad33' in result[4]
        assert  result[4]['https://www.productreview.com.au/reviews/4d0efe70-272a-5933-a2c3-d8a8794dad33']['title'] == 'Home Sweet Home'
        assert 'content' in result[4]['https://www.productreview.com.au/reviews/4d0efe70-272a-5933-a2c3-d8a8794dad33']
        assert result[4]['https://www.productreview.com.au/reviews/4d0efe70-272a-5933-a2c3-d8a8794dad33']['author_name'] == 'CLAC'
        assert result[4]['https://www.productreview.com.au/reviews/4d0efe70-272a-5933-a2c3-d8a8794dad33']['author_uri'] == 'https://www.productreview.com.au/consumer-profiles/65f4f022-841a-5d4d-ac46-2f7cc23c7dac'
        assert result[4]['https://www.productreview.com.au/reviews/4d0efe70-272a-5933-a2c3-d8a8794dad33']['rating'] == 5
        assert result[4]['https://www.productreview.com.au/reviews/4d0efe70-272a-5933-a2c3-d8a8794dad33']['date'] == '2022-04-08T05:13:20Z'

    def test_parse_html_2(self):
        with open('./testdata/reviews_present_2.html', mode='r', encoding='utf8') as f:
            html = f.read()
        result = api.parse_html(html, True, 'test_url', 'Completed, status code 200')
        assert type(result) == tuple
        assert len(result) == 5
        assert result[0] == 'Completed, status code 200'
        assert result[1] == 'Page test_url: reviewCount=164; extracted from page: 25'
        assert result[2] == 164
        assert result[3] == [0, 0, 0, 12, 152]
        assert type(result[4]) == dict
        assert 'https://www.productreview.com.au/reviews/7398d975-49f1-560a-a807-30a03a3bdc2e' in result[4]
        assert  result[4]['https://www.productreview.com.au/reviews/7398d975-49f1-560a-a807-30a03a3bdc2e']['title'] == 'Game changer'
        assert 'content' in result[4]['https://www.productreview.com.au/reviews/7398d975-49f1-560a-a807-30a03a3bdc2e']
        assert result[4]['https://www.productreview.com.au/reviews/7398d975-49f1-560a-a807-30a03a3bdc2e']['author_name'] == 'Sarah'
        assert result[4]['https://www.productreview.com.au/reviews/7398d975-49f1-560a-a807-30a03a3bdc2e']['author_uri'] == 'https://www.productreview.com.au/consumer-profiles/6c4dd0f8-86af-5128-a760-125e08ba04ad'
        assert result[4]['https://www.productreview.com.au/reviews/7398d975-49f1-560a-a807-30a03a3bdc2e']['rating'] == 5
        assert result[4]['https://www.productreview.com.au/reviews/7398d975-49f1-560a-a807-30a03a3bdc2e']['date'] == '2022-04-11T10:51:54Z'

    def test_parse_html_3(self):
        with open('./testdata/reviews_absent.html', mode='r', encoding='utf8') as f:
            html = f.read()
        result = api.parse_html(html, True, 'test_url', 'Completed, status code 200')
        assert result == ('Completed, status code 200', 'Page test_url: reviewCount=164; extracted from page: 0', 164, [0, 0, 0, 12, 152], {})

    def test_parse_html_4(self):
        with open('./testdata/challenge_page.html', mode='r', encoding='utf8') as f:
            html = f.read()
        result = api.parse_html(html, True, 'test_url', 'Completed, status code 200')
        assert result == ('Completed, status code 200', 'Page is invalid: test_url', 0, [], {})

    def test_get_reviews_from_page_ok(self):
        url = 'https://www.productreview.com.au/listings/expert-electrical'
        retry_on_rate_limit = False
        get_ssr_data = True
        result = api.get_reviews_from_page(url, retry_on_rate_limit, get_ssr_data)
        assert type(result) == tuple
        assert len(result) == 5
        assert type(result[0]) == str
        assert type(result[1]) == str
        assert type(result[2]) == int
        assert type(result[3]) == list
        assert type(result[4]) == dict
        assert result[0] == 'Completed, status code 200'
        assert len(result[4]) == 25
        k = list(result[4].keys())[0]
        assert 'title' in result[4][k]
        assert 'content' in result[4][k]
        assert 'author_name' in result[4][k]
        assert 'author_uri' in result[4][k]
        assert 'rating' in result[4][k]
        assert 'date' in result[4][k]

    def test_get_reviews_from_page_failed(self):
        url = 'https://www.productreview.com.au'
        retry_on_rate_limit = False
        get_ssr_data = True
        result = api.get_reviews_from_page(url, retry_on_rate_limit, get_ssr_data)
        assert type(result) == tuple
        assert len(result) == 5
        assert type(result[0]) == str
        assert type(result[1]) == str
        assert type(result[2]) == int
        assert type(result[3]) == list
        assert type(result[4]) == dict
        assert result[0] == 'Completed, status code 200'
        assert result[1] == 'Page is invalid: %s' % url
        assert result[2] == 0
        assert result[3] == []
        assert result[4] == {}

    def test_page_url(self):
        base_url = 'https://some.url.com'
        assert api.page_url(base_url, 4, 1, False) == '%s?rating=4' % (base_url)
        assert api.page_url(base_url, 3, 5, False) == '%s?rating=3&page=5' % (base_url)
        assert api.page_url(base_url, 5, 1, True) == '%s?sortBy=oldest&rating=5' % (base_url)
        assert api.page_url(base_url, 2, 6, True) == '%s?sortBy=oldest&rating=2&page=6' % (base_url)

    def test_get_reviews_single_page(self):
        url = 'https://www.productreview.com.au/listings/hotondo-homes'
        crawl = False
        result = api.get_reviews(url, crawl)
        assert type(result) == dict
        assert len(result) == 3
        assert 'http_response' in result
        assert 'job_status' in result
        assert 'data' in result
        assert result['http_response'] == 'Completed, status code 200'
        assert url in result['job_status']
        assert 'extracted from page' in result['job_status']
        assert len(result['data']) == 25
        k = list(result['data'].keys())[0]
        assert 'title' in result['data'][k]
        assert 'content' in result['data'][k]
        assert 'author_name' in result['data'][k]
        assert 'author_uri' in result['data'][k]
        assert 'rating' in result['data'][k]
        assert 'date' in result['data'][k]

    def test_get_reviews_multiple_pages(self):
        url = 'https://www.productreview.com.au/listings/hotondo-homes'
        crawl = True
        sort_by_oldest = True
        retry_on_rate_limit = True
        page_limit = 2
        result = api.get_reviews(url, crawl, sort_by_oldest, retry_on_rate_limit, page_limit)
        assert type(result) == dict
        assert len(result) == 3
        assert 'http_response' in result
        assert 'job_status' in result
        assert 'data' in result
        assert result['http_response'] == 'Completed, status code 200'
        assert url in result['job_status']
        assert 'extracted from page' in result['job_status']
        assert len(result['data']) >= 25
        k = list(result['data'].keys())[0]
        assert 'title' in result['data'][k]
        assert 'content' in result['data'][k]
        assert 'author_name' in result['data'][k]
        assert 'author_uri' in result['data'][k]
        assert 'rating' in result['data'][k]
        assert 'date' in result['data'][k]

    def test_run_job(self):
        def test_method(parameter1, parameter2):
            return parameter1, parameter2, parameter1 + parameter2
        api.run_job('1', test_method, 1, 2)
        assert api.JOBS['1'] == (1, 2, 3)

if __name__ == '__main__':
    unittest.main()
