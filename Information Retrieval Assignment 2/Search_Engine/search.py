from elasticsearch import Elasticsearch

total_doc = 3000
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


def xor(a, b):
    return list(set(a) ^ set(b))


def get_measurement(precision, recall):
    avg_precision = 0.0
    avg_recall = 0.0
    c = 0
    for k in range(total_doc):
        if all_attempt[k] == 'relevant':
            precision += 1.0
            recall += 1.0
            temp_precision = precision / (k + 1)
            avg_precision += temp_precision
            temp_recall = recall / total_doc
            temp_precision = round(temp_precision, 8)
            temp_recall = round(temp_recall, 8)
            avg_recall += temp_recall
            print("@K", k + 1, "| P=", temp_precision, "| R=", temp_recall, "Found document id:", hit_order[c])
            c += 1
        else:
            temp_precision = precision / (k + 1)
            temp_recall = recall / total_doc
            avg_precision += temp_precision
            avg_recall += temp_recall
            temp_precision = round(temp_precision, 8)
            temp_recall = round(temp_recall, 8)
            print("@K", k + 1, "| P=", temp_precision, "| R=", temp_recall)
    print("Precision AVG. =>", avg_precision / total_doc)
    print("Recall AVG =>", avg_recall / total_doc)


print(
    "Selection searching for document menu base on...:"
    "\n1.'Media-type' and 'Content' keyword in range of 'Published' date"
    "\n2.'Title' name in range of 'Published' date"
    "\n3.Specific 'Source' of all time"
    "\n4.Specific keyword in 'Content' of all time"
    "\n5.Exact keyword in 'Title'"
    "\n6.Begin letter of 'Source'"
    "\n7.Keyword for 'Title' or 'Content' but title will be more important than content")
select = input("\nEnter Choice:")
if select == '1':
    media_query = input("Media-type:")
    content_query = input("Content keyword:")
    start_date_query = input("Published start date (yyyy/mm/dd):")
    end_date_query = input("Published end date (yyyy/mm/dd):")
    res = es.search(index="news_article", doc_type="articles", body=
    {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase_prefix": {
                            "content": content_query
                        }
                    },
                    {
                        "match_phrase_prefix": {
                            "media-type": media_query
                        }
                    },
                    {
                        "range": {
                            "published": {
                                "gte": start_date_query,
                                "lte": end_date_query,
                                "format": "yyyy/MM/dd||yyyy"
                            }
                        }
                    }
                ]
            }
        }
    }
                    , size=total_doc)

if select == '2':
    title_query = input("Title-name (Pre-fix):")
    start_date_query = input("Published start date (yyyy/mm/dd):")
    end_date_query = input("Published end date (yyyy/mm/dd):")
    res = es.search(index="news_article", doc_type="articles", body=
    {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase_prefix": {
                            "title": title_query
                        }
                    },
                    {
                        "range": {
                            "published": {
                                "gte": start_date_query,
                                "lte": end_date_query,
                                "format": "yyyy/MM/dd||yyyy"
                            }
                        }
                    }
                ]
            }
        }
    }
                    , size=total_doc)

if select == '3':
    source_query = input("Source name (Pre-fix):")
    res = es.search(index="news_article", doc_type="articles", body=
    {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase_prefix": {
                            "source": source_query
                        }
                    }
                ]
            }
        }
    }
                    , size=total_doc)

if select == '4':
    content_query = input("Content (Keyword):")
    res = es.search(index="news_article", doc_type="articles", body=
    {
        "query": {
            "bool": {
                "must": [
                    {
                        "match": {
                            "content": content_query
                        }
                    }
                ]
            }
        }
    }
                    , size=total_doc)

if select == '5':
    title_query = input("Title (Exact keyword):")
    res = es.search(index="news_article", doc_type="articles", body=
    {
        "query": {
            "term": {
                "title": title_query
            }
        }
    }
                    , size=total_doc)

if select == '6':
    source_query = input("Begin source letter:")
    source_query = source_query + "*"
    res = es.search(index="news_article", doc_type="articles", body=
    {
        "query": {
            "wildcard": {
                "source": source_query
            }
        }
    }

                    , size=total_doc)

if select == '7':
    key_query = input("Keyword:")
    res = es.search(index="news_article", doc_type="articles", body=
    {
        "query": {
            "multi_match": {
                "query": key_query,
                "fields": ["title^3", "content"]
            }

        }
    }

                    , size=total_doc)

add_ele = [res['took'], res['timed_out'], res['_shards'], res['hits']]
counter = 1
hits = len(res['hits']['hits'])
print("\nNumber of document in database:", total_doc)
print("Found :", hits)
for doc in res['hits']['hits']:
    print("\n==========================================", counter, "/", len(res['hits']['hits']),
          "==================================================")
    counter += 1
    print("Document ID:", doc['_id'])
    print("Search score:", doc['_score'])
    print("Media type:", doc['_source']['media-type'])
    print("Title:", doc['_source']['title'])
    print("From source:", doc['_source']['source'])
    print("Published:", doc['_source']['published'])
    print("Content:", doc['_source']['content'], "\n")

all_attempt = list(range(1, total_doc + 1))
time_attempt = []
for doc in res['hits']['hits']:
    time_attempt.append((doc['_id']))

time_attempt = [int(x) for x in time_attempt]
time_attempt.sort()
hit_order = time_attempt
doc_found = time_attempt
binary_mapping = xor(time_attempt, all_attempt)

for i in range(total_doc):
    for x in time_attempt:
        if x == i + 1:
            all_attempt[i] = 'relevant'
    for y in binary_mapping:
        if y == i + 1:
            all_attempt[i] = 'none'

print("\nRANKED RETRIEVAL")
get_measurement(0.00, 0.00)
