import os

template = open('base_collector_template.py', 'r', encoding='utf-8').read()

publishers = [
    {'file': 'odisha_bhaskar_collector.py', 'url': 'https://odishabhaskar.in/category/odisha/', 'domain': 'odishabhaskar.in', 'name': 'ODISHA BHASKAR'},
    {'file': 'prajatantra_collector.py', 'url': 'https://prajatantra.in/', 'domain': 'prajatantra.in', 'name': 'PRAJATANTRA'},
    {'file': 'kalinga_tv_collector.py', 'url': 'https://kalingatv.com/state/', 'domain': 'kalingatv.com', 'name': 'KALINGA TV'},
    {'file': 'argus_news_collector.py', 'url': 'https://argusnews.in/category/odisha', 'domain': 'argusnews.in', 'name': 'ARGUS NEWS'},
    {'file': 'naxatra_news_collector.py', 'url': 'https://naxatranews.com/category/odisha/', 'domain': 'naxatranews.com', 'name': 'NAXATRA NEWS'},
    {'file': 'hindu_collector.py', 'url': 'https://www.thehindu.com/news/national/other-states/', 'domain': 'thehindu.com', 'name': 'THE HINDU'},
    {'file': 'ht_collector.py', 'url': 'https://www.hindustantimes.com/cities/others', 'domain': 'hindustantimes.com', 'name': 'HINDUSTAN TIMES'},
    {'file': 'indian_express_collector.py', 'url': 'https://indianexpress.com/about/odisha/', 'domain': 'indianexpress.com', 'name': 'THE INDIAN EXPRESS'}
]

for p in publishers:
    content = template.replace('https://www.dharitri.com/category/odisha/', p['url'])
    content = content.replace('dharitri.com', p['domain'])
    content = content.replace('DHARITRI NAYAGARH COLLECTOR', f"{p['name']} COLLECTOR")
    content = content.replace('Dharitri', p['name'])
    open(f'app/collectors/{p["file"]}', 'w', encoding='utf-8').write(content)
