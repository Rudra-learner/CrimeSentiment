import importlib
import sys
sys.path.append('d:/CrimeSentimentProject')

collectors = [
    'odisha_tv_collector', 'orissa_post', 'kanak_collector', 'pragativadi_collector', 
    'prameya_news', 'ndtv_collector', 'samaja_collector', 'toi_collector', 
    'dharitri_collector', 'odisha_bhaskar_collector', 'prajatantra_collector', 
    'kalinga_tv_collector', 'argus_news_collector', 'naxatra_news_collector', 
    'hindu_collector', 'ht_collector', 'indian_express_collector'
]

results = {}

for c in collectors:
    try:
        mod = importlib.import_module(f'app.collectors.{c}')
        if hasattr(mod, 'collect_article_urls'):
            urls = mod.collect_article_urls()
        elif hasattr(mod, 'collect_urls'):
            if c == 'kanak_collector':
                urls = mod.collect_urls('odisha')
            else:
                urls = mod.collect_urls()
        else:
            urls = []
        print(f'{c}: {len(urls)}')
    except Exception as e:
        print(f'{c}: ERROR {e}')
