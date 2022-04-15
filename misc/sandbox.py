import json

with open('section.xml', mode='r', encoding='utf8') as i:
    content = i.read()
    s_data = content.split('<script data-react-helmet="true" type="application/ld+json">')[1].split('</script>')[0]

j_data = json.loads(s_data)

print(len(j_data['review']))
print(j_data['review'][0])



