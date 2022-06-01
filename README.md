# Coding challenge from ReviewTrackers

## Objective

- Retrieve review data from https://www.productreview.com.au
- Service must take in URL in form https://www.productreview.com.au/listings/page and return review data from specified page

## Endpoints
---
### /

<details>
<summary><b>GET</b></summary>

Synchronously returns data acquired from page at the specified URL.

| parameter | description             |
|-----------|-------------------------|
| url       | URL of a page to scrape. Must begin with https://www.productreview.com.au/listings/ |

<details>
<summary>Sample response</summary>

```
{
    "http_response": "Completed, status code 200",
    "job_status": "Page https://www.productreview.com.au/listings/expert-electrical: reviewCount=272; extracted from page: 25",
    "data": {
        "https://www.productreview.com.au/reviews/035a828d-2d6d-5efa-a8fd-30fb19b2f111": {
            "author_name": "Andrezza L.",
            "author_uri": "https://www.productreview.com.au/consumer-profiles/e6a711c7-2d7e-4bc9-9bff-cf3212aa1d5f",
            "content": "From first contact by email, I could see staff was very polite and keen to offer the best service.\nHad a visit from Zac for a quote, and he was on time, very knowledgeable, polite and best of all: not \"pushy\".\nInstallation team was also on time. They were very polite and had a big smile even working on a cold and rainy day.\nThe whole process was smooth and easy.\nHighly recommend!",
            "date": "2022-05-20T12:44:54Z",
            "rating": 5,
            "title": "Excellent service from beginning till the  end."
        },
        "https://www.productreview.com.au/reviews/0635b08e-9c60-5b90-93e5-7500e16ddf84": {
            "author_name": "Hannah pascoe",
            "author_uri": "https://www.productreview.com.au/consumer-profiles/75d2b9f6-5a74-5f22-91d3-3e40ec5f9800",
            "content": "Great customer service. Friendly, honest staff. Very helpful through the whole process. Definitely felt in safe hands and would recommend to anyone considering solar. We love our new system. Thanks expert electrical",
            "date": "2022-05-22T08:48:46Z",
            "rating": 5,
            "title": "Highly recommend this company"
        },
        "https://www.productreview.com.au/reviews/0bebac20-2a9c-50ff-ae89-44ce7859f672": {
            "author_name": "Zina C",
            "author_uri": "https://www.productreview.com.au/consumer-profiles/f4156941-0f0b-5f41-b669-cbf2f31aa9a0",
            "content": "Professional and efficient!\nThank you Expert Electrical, your team are a breath of fresh air. Quick and easy turn around. Everyone I spoke to was helpful and friendly - rare to find these days! Will not hesitate to recommend to friends and family.\nMario & Zina (Aspley Qld)",
            "date": "2022-04-12T11:14:56Z",
            "rating": 5,
            "title": "Professional and Efficient"
        },
        ...
    }
}
```

</details>
</details>

<details>
<summary><b>POST</b></summary>

Starts asynchronous job to acquire data from page at the specified URL and returns endpoint to fetch results at.

| parameter           | description                                                                                   |
|---------------------|-----------------------------------------------------------------------------------------------|
| url                 | URL of a page to scrape. Must begin with https://www.productreview.com.au/listings/           |
| crawl               | If present and is true, we will process multiple pages with same base URL                     |
| oldest_first        | If present and is true, we will sort pages oldest-to-newest when we need crawling             |
| retry_on_rate_limit | If present and is true, we will wait and retry when we encounter rate limit                   |
| page_limit          | If present and is greater than 0, we will not process more pages than specified when crawling |

<details>
<summary>Sample response</summary>

```
{
    "fetch_results_at": "/result?job_id=1654059374.17291"
}
```

</details>
</details>

---
### /jobs

<details>
<summary><b>GET</b></summary>

Returns list of asynchronous jobs.

<details>
<summary>Sample response</summary>

```
{
    "jobs": [
        "1654059374.17291"
    ]
}
```

</details>
</details>

---
### /result

<details>
<summary><b>GET</b></summary>

Returns data retrieved by an asynchronous job.

| parameter | description                                |
|-----------|--------------------------------------------|
| job_id    | ID of a job whose result is to be returned |

<details>
<summary>Sample response</summary>

```
{
    "http_response": "Completed, status code 200",
    "job_status": "Page https://www.productreview.com.au/listings/expert-electrical: reviewCount=272; extracted from page: 25"
    "data": {
        "https://www.productreview.com.au/reviews/035a828d-2d6d-5efa-a8fd-30fb19b2f111": {
            "author_name": "Andrezza L.",
            "author_uri": "https://www.productreview.com.au/consumer-profiles/e6a711c7-2d7e-4bc9-9bff-cf3212aa1d5f",
            "content": "From first contact by email, I could see staff was very polite and keen to offer the best service.\nHad a visit from Zac for a quote, and he was on time, very knowledgeable, polite and best of all: not \"pushy\".\nInstallation team was also on time. They were very polite and had a big smile even working on a cold and rainy day.\nThe whole process was smooth and easy.\nHighly recommend!",
            "date": "2022-05-20T12:44:54Z",
            "rating": 5,
            "title": "Excellent service from beginning till the  end."
        },
        "https://www.productreview.com.au/reviews/0635b08e-9c60-5b90-93e5-7500e16ddf84": {
            "author_name": "Hannah pascoe",
            "author_uri": "https://www.productreview.com.au/consumer-profiles/75d2b9f6-5a74-5f22-91d3-3e40ec5f9800",
            "content": "Great customer service. Friendly, honest staff. Very helpful through the whole process. Definitely felt in safe hands and would recommend to anyone considering solar. We love our new system. Thanks expert electrical",
            "date": "2022-05-22T08:48:46Z",
            "rating": 5,
            "title": "Highly recommend this company"
        },
        "https://www.productreview.com.au/reviews/0bebac20-2a9c-50ff-ae89-44ce7859f672": {
            "author_name": "Zina C",
            "author_uri": "https://www.productreview.com.au/consumer-profiles/f4156941-0f0b-5f41-b669-cbf2f31aa9a0",
            "content": "Professional and efficient!\nThank you Expert Electrical, your team are a breath of fresh air. Quick and easy turn around. Everyone I spoke to was helpful and friendly - rare to find these days! Will not hesitate to recommend to friends and family.\nMario & Zina (Aspley Qld)",
            "date": "2022-04-12T11:14:56Z",
            "rating": 5,
            "title": "Professional and Efficient"
        },
        ...
    }
}
```

</details>
</details>
