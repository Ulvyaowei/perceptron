#!/usr/bin/python
# _*_ coding:utf-8 _*_
import urllib
from bs4 import BeautifulSoup
from urllib import request
import ssl
import re
import os.path
from nltk.tag import StanfordNERTagger
import nltk
from itertools import chain,groupby
import numpy as np
from nltk import word_tokenize,collocations,pos_tag_sents,sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer,TfidfTransformer,CountVectorizer
from nltk.chunk import tree2conlltags
from nltk.chunk.regexp import RegexpParser
import operator
from unidecode import unidecode

def get_text(url):
    links = []
    html = urllib.request.urlopen(url).read().decode('UTF8')
    soup = BeautifulSoup(html,'html.parser')
    text = soup.get_text()
    for i in soup.findAll('a', attrs={'href': re.compile("^http://")}):
        links.append(i.get('href'))
    if os.path.exists('word_log.txt'):
        f = open('word_log.txt','w',encoding='UTF8')
    else:
        f = open('word_log.txt','x',encoding='UTF8')
        f = open('word_log.txt','w',encoding='UTF8')
    f.write(text)
    return text

def get_tokens(text):
    word_list = []
    voc = []
    voc_write = ''
    sent = sent_tokenize(text)
    word_single = word_tokenize(text)
    if os.path.exists('token_log.txt'):
        k = open('token_log.txt','w',encoding='UTF8')
    else:
        k = open('token_log.txt','x',encoding='UTF8')
        k = open ( 'token_log.txt', 'w', encoding='UTF8' )
    k.write(str(word_single))
    for i in sent:
        word = word_tokenize(i)
        words = list(map(lambda s: s.lower(),word))
        word_list.append(words)
    words_pos = pos_tag_sents(word_list)

    if os.path.exists('pos_log.txt'):
        f = open('pos_log.txt','w',encoding='UTF8')
    else:
        f = open('pos_log.txt','x',encoding='UTF8')
        f = open ( 'pos_log.txt', 'w', encoding='UTF8' )
    f.write(str(words_pos))

    grammar = r'KT: ' \
              r'{' \
              r'(<JJ>* <NN.*>+ <In>)? <JJ>* <NN.*>+' \
              r'}'
    grammar = RegexpParser(grammar)

    tags = chain.from_iterable([tree2conlltags(grammar.parse(tag)) for tag in words_pos])

    for key, group in groupby(tags, lambda tag: tag[2] != 'O'):
        voc_temp = ' '.join([word for (word,pos,chunk) in group])
        if key is True and voc_temp not in stopwords.words('english') and voc_temp != 'https':
            voc.append(voc_temp)
            voc_write += voc_temp
            voc_write += '\n'
    if os.path.exists('voc_log.txt'):
        f = open('voc_log.txt','w',encoding='UTF8')
    else:
        f = open('voc_log.txt','x',encoding='UTF8')
        f = open('voc_log.txt','w',encoding='UTF8')
    f.write(voc_write)
    return voc

def get_NER(text):
    st = StanfordNERTagger('english.all.3class.distsim.crf.ser','stanford-ner.jar',encoding='UTF8')
    tokens = word_tokenize(text)
    NER_text = st.tag(tokens)
    if os.path.exists('NER_log.txt'):
        f = open('NER_log.txt','w',encoding='UTF8')
    else:
        f = open('NER_log.txt','x',encoding='UTF8')
        f = open('NER_log.txt','w',encoding='UTF8')
    for i in NER_text:
        if i[1] != 'O':
            f.write(str(i))
    return NER_text

def tf_idf_model(texts):
    text = [get_tokens(unidecode(i)) for i in texts]
    text = list(chain(*text))
    text = list(np.unique(text))

    print("The most Frequent 15 Words and Phrases:\n")

    max_text_len = max(map(lambda s: len(s.split(' ')),text))
    model = TfidfVectorizer(vocabulary=text,lowercase=True,ngram_range=(1,max_text_len),
                            stop_words=None,min_df=1,max_df=0.9)
    X = model.fit_transform(texts)
    text_sort = [v[0] for v in sorted(model.vocabulary_.items(),key=operator.itemgetter(1))]

    sort_array = np.fliplr(np.argsort(X.toarray()))

    #possible phrase
    key_phrases = list()
    for i in sort_array:
        key_phrase = [text_sort[e] for e in i[0:15]]
        key_phrases.append(key_phrase)
    return key_phrases

def tf_idf(words):
    data = [words]
    weight = ''
    vector = CountVectorizer()
    X = vector.fit_transform(data)
    word = vector.get_feature_names()
    transformer = TfidfTransformer()
    tf = transformer.fit_transform(X)
    w = tf.toarray()

    for i in range(len(w)):
        data_map = {}
        for j in range(len(word)):
            data_map[word[j]] = w[i][j]
    sorted_map = sorted(data_map.items(),key=lambda item: item[1],reverse=True)

    for k in sorted_map:
        weight += str(k)
        weight += '\n'

    if os.path.exists('TF_IDF_log.txt'):
        f = open('TF_IDF_log.txt','w',encoding='UTF8')
    else:
        f = open('TF_IDF_log.txt','x',encoding='UTF8')
        f = open('TF_IDF_log.txt','w',encoding='UTF8')
    f.write(weight)

def read_file(path):
    with open(path,'r') as file:
        return file.read()
clear_text = []
def main():
    print("Please Enter Your Websites:")
    ssl._create_default_https_context = ssl._create_unverified_context
    url = input()
    clear_text.append(get_text(url))
    text = [clear_text[0]]
    key_phrase = tf_idf_model(text)
    i = 0
    update_text = 'The Most 15 Frequent Keywords and Key Phrases\n'
    while i<15:
        update_text += key_phrase[0][i]
        update_text += '\n'
        print(i+1,'.',key_phrase[0][i])
        i+=1
    tf_idf(read_file('voc_log.txt'))
    if os.path.exists('top_index.txt'):
        f = open('top_index.txt','w',encoding='UTF8')
    else:
        f = open('top_index.txt','x',encoding='UTF8')
        f = open('top_index.txt','w',encoding='UTF8')
    f.write(update_text)
    print("\nPlease Check the word_log.txt for the raw text from the URL")
    print ( "\nPlease Check the token_log.txt for the tokens" )
    print("\nPlease Check the NER_log.txt for the Name Entity Recognition")
    print("\nPlease Check voc_log.txt for the phrases")
    print ( "\nPlease pos_log.txt for the pos_tag" )



main()
