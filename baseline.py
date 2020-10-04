import numpy as np
import re
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import argparse


def LDA_get_top_words(input_doc, top_n, n_topics=10):
    tf_vectorizer = CountVectorizer(max_features=None,
                                token_pattern=r"\b[^\n ' ']+\b",
                                stop_words=None)
    tf = tf_vectorizer.fit_transform(input_doc)
    lda = LatentDirichletAllocation(n_components=n_topics, 
                                max_iter=100,
                                learning_method='batch')
    lda.fit(tf)
    feature_names = tf_vectorizer.get_feature_names()
    result_str = ''
    for topic_index, topic in enumerate(lda.components_):
        top_x = min(top_n, topic.size)
        for i in topic.argsort()[:-top_x - 1:-1]:
            result_str += feature_names[i] + '; '
    return result_str

def tfIdf_get_top_words(input_doc, top_n):
    tiv = TfidfVectorizer(token_pattern=r"\b[^\n ' ']+\b")
    tiv_fit = tiv.fit_transform(input_doc)
    matrix = tiv_fit.toarray()
    result_keywords_list = []
    for i in range(matrix.shape[0]):
        sorted_keyword = sorted(zip(tiv.get_feature_names(), matrix[i]), key=lambda x:x[1], reverse=True)
        top_x = min(top_n, len(sorted_keyword))
        result_keywords = [w for w in sorted_keyword[:top_x]]
        result_keywords_list.append(result_keywords)
    result_str = ''
    for doc in result_keywords_list:
        for line in doc:
            result_str += line[0] + '; '
    return result_str

'''
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help='input file')
    parser.add_argument('-o', help='output result')
    parser.add_argument('-t', help='type of algorithm')
    parser.add_argument('-n', help='top n words', type=int, default=10)
    parser.add_argument('-re', help='exclude_re', default=None)
    args = parser.parse_args()
    input_str = preprocess(args.i, args.re)
    if args.t == 'lda':
        LDA_get_top_words(input_str, args.o, args.n)
        print(args.i + ' lda finished')
    if args.t == 'tfidf':
        tfIdf_get_top_words(input_str, args.o, args.n)
        print(args.i + ' tfidf  finished')
'''

