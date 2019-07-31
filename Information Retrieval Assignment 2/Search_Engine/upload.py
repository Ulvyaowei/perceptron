import json_lines
import json
from elasticsearch import Elasticsearch


es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
with open('sample-1M.jsonl', 'rb') as f:
    i = 1
    for ele in json_lines.reader(f):
        if i > 3000:
            continue
        else:
            ele = json.dumps(ele)
            decode = json.loads(ele)
            es.index(index='news_article', doc_type='articles', id=i, body=decode)
        i += 1
