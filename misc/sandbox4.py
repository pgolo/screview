import json
import requests
from bs4 import BeautifulSoup

url = 'https://www.productreview.com.au/listings/hotondo-homes?page=10'

response = requests.get(url)
content = response.text

print(response.status_code)

soup = BeautifulSoup(content, 'html.parser')
inputs = {}
post_url = soup.form['action']
for input in soup.form.find_all('input'):
    inputs[input.get('name')] = input.get('value')

print(post_url)
response2 = requests.post('https://www.productreview.com.au' + post_url, inputs)
print(response2.text)

"""

challenge_form = content.split('<form class="challenge-form" id="challenge-form"')[1].split('</form>')[0]
post_url = challenge_form.split('action="')[1].split('"')[0]
s_inputs = challenge_form.split('<input ')[1:]
inputs = [{x.split('name="')[1].split('"')[0]: x.split('value="')[1].split('"')[0] if 'value' in x else ''} for x in s_inputs]

#print(challenge_form)
#print(post_url)
for i in inputs:
    print(i)

"""
