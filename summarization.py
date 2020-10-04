from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import json
import gensim
import numpy as np
import heapq
import pandas as pd
import re

import baseline
import matchTree
import evaluate
import utils
evaluation = ['precision', 'recall', 'f_score', 'compression_rate']

def get_tri_data_from_groundTruth(docs, skip_var, triplets, templates):
    matcher = matchTree.MatchTree()
    for t in templates:
        matcher.add_template(t.split())
    index = 0
    tri_data = {}
    for logs in docs:
        count = 1
        tri_data[index] = {}
        for log in logs:
            tri_data[index][count] = []
            tri_data[index][count].append(log)
            match_index = None
            try:
                match_index = matcher.match_template(log.split())[0]
            except:
                print(log)
                continue
            temp_triplets = []
            for i in triplets[match_index-1]:
                temp_triplet = []
                skip_flag = False
                is_flag = False
                for t in i:
                    if 'VAR' in t:
                        if skip_var:
                            skip_flag = True
                            break
                        else:
                            temp_str = re.sub('VAR[^\s]*', '', t)
                            temp_str = re.sub('  ', ' ', temp_str)
                            temp_str = temp_str.strip()
                            temp_triplet.append(temp_str)
                            continue
                    if 'is' == t:
                        is_flag = True
                        break
                    temp_triplet.append(t)
                if (not skip_var or not skip_flag) and (not is_flag):
                    temp_triplets.append(temp_triplet)
            tri_data[index][count].append(temp_triplets)
            count += 1
        index += 1
    return tri_data

def load_model(filename, is_binary=False):
    model = gensim.models.KeyedVectors.load_word2vec_format(filename, binary = is_binary)
    return model

def get_triplet(tri_data:dict):
    '''
    input: tri_data, the json format of triplets data
    output: tri_list, the list of triplet
            tri_to_sen, dict. mapping triplets to sentence
            sen_to_triSet, dict. mapping sentence to the corresponding triplet set
    '''
    tri_to_sen = dict()
    sen_to_triSet = dict()
    tri_list = []
    for index in tri_data:
        sentence = tri_data[index][0]
        triplets = tri_data[index][1]
        sen_to_triSet[sentence] = triplets
        for triplet in triplets:
            str_triplet = ' '.join(triplet).strip()
            if len(str_triplet) == 0:
                continue
            tri_to_sen[str_triplet] = sentence
            tri_list.append(str_triplet)
    return tri_list, tri_to_sen, sen_to_triSet

def get_vector(word_model, dimension:int, tri_list:list):
    index_to_triplet = {}
    index_to_vector = {}
    triplet_record = set()
    index = 0
    for triplet in tri_list:
        if triplet in triplet_record:
            continue
        triplet_record.add(triplet)    
        vector = np.zeros(dimension)
        for word in triplet.split():
            if word in word_model:
                vector += word_model[word]
            else:
                #print(word)
                continue
        vector /= len(triplet)
        if not vector.any():
            continue
        index_to_triplet[index] = triplet
        index_to_vector[index] = vector
        index += 1
    return index_to_triplet, index_to_vector

def get_matrix(index_to_vector):
    mat_length = len(index_to_vector)
    sim_mat = np.zeros([mat_length, mat_length])
    for x_index in range(mat_length):
        for y_index in range(mat_length):
            sim_mat[x_index][y_index] = cosine_similarity(index_to_vector[x_index].reshape(1,-1), 
                                                          index_to_vector[y_index].reshape(1,-1))
    for index in range(mat_length):
        sim_mat[index][index] = 0
    return sim_mat

def textRank(sim_mat, topk, index_to_triplet):
    summary = ''
    nx_graph = nx.from_numpy_array(sim_mat)
    #scores = nx.pagerank(nx_graph, max_iter=1000, tol=0.1, weight='weight') #tol=0.24
    scores = nx.pagerank_numpy(nx_graph, weight='weight')
    result = heapq.nlargest(topk, scores.items(), key=lambda x:x[1])
    for i in result:
        index = i[0]
        triplet = index_to_triplet[index]
        summary += triplet + '; '
    return summary

def pipeline(elem_list, word_model, topK):
    dimension = word_model.vector_size
    index_to_elem, index_to_vector = get_vector(word_model, dimension, elem_list)
    hy = ''
    if len(index_to_elem) < topK:
        for i in index_to_elem:
            hy += index_to_elem[i] + '; '
    else:
        sim_mat = get_matrix(index_to_vector)
        hy = textRank(sim_mat, topK, index_to_elem)
    return hy.strip()

def evaluate_all(log_type:str, word_model, topK):
    pd_result = {'tf-idf':[], 'LDA':[], 'sentence textRank':[], 'triplet textRank':[]}
    log_path = 'data/logs/'+log_type+'.txt'
    template_path = 'data/template/'+log_type+'Template.json'
    summary, docs, templates, triplets = utils.load_data(log_path, template_path, 0, log_type)
    tri_data = get_tri_data_from_groundTruth(docs, 0, triplets, templates)
    eval_LDA = evaluate.eval_unigram()
    eval_tfIdf = evaluate.eval_unigram()
    eval_triRank = evaluate.eval_unigram()
    eval_senRank = evaluate.eval_unigram()
    for index in range(len(docs)):
        gt = summary[index].strip()
        doc_length = len(''.join(docs[index]))
        hy = baseline.LDA_get_top_words([' '.join(docs[index])], topK, n_topics=5)
        hy_length = len(hy)
        eval_LDA.evaluate_unigram(gt.replace(';',''), hy.replace(';',''))
        eval_LDA.record_compression_rate(hy_length, doc_length)

        hy = baseline.tfIdf_get_top_words([' '.join(docs[index])], topK)
        hy_length = len(hy)
        eval_tfIdf.evaluate_unigram(gt.replace(';',''), hy.replace(';',''))
        eval_tfIdf.record_compression_rate(hy_length, doc_length)

        tri_list, tri_to_sen, sen_to_triSet = get_triplet(tri_data[index])
        hy = pipeline(tri_list, word_model, topK)
        hy_length = len(hy)
        eval_triRank.evaluate_unigram(gt.replace(';',''), hy.replace(';',''))
        eval_triRank.record_compression_rate(hy_length, doc_length)

        hy = pipeline(docs[index], word_model, topK)
        hy_length = len(hy)
        eval_senRank.evaluate_unigram(gt.replace(';',''), hy.replace(';',''))
        eval_senRank.record_compression_rate(hy_length, doc_length)

    for i in evaluation:
        pd_result['LDA'].append(eval_LDA.get_result()[i])
        pd_result['tf-idf'].append(eval_tfIdf.get_result()[i])
        pd_result['triplet textRank'].append(eval_triRank.get_result()[i])
        pd_result['sentence textRank'].append(eval_senRank.get_result()[i])
    return pd_result

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--evaluate', help='evaluate mode', type=int, default=0)
    parser.add_argument('--type', help="[ONLY needed in evaluate mode]log tyoe", type=str)
    parser.add_argument('--model', help='the word2vec model path', type=str)
    parser.add_argument('--topk', help="topK triplets will be extracted", type=int)

    parser.add_argument('--triplet', help='[NOT needed in evaluate mode]triplet path', type=str)
    parser.add_argument('--output', help="the output for result", type=str, default=None)


    args = parser.parse_args()
    topk=args.topk
    word_model=load_model(args.model)
    if args.evaluate == 1:
        log_type = args.type
        pd_result = evaluate_all(log_type, word_model, topk)
        print(pd.DataFrame.from_dict(pd_result, orient='index', columns=evaluation))
        if args.output != None:
            with open(args.output, 'w') as ofile:
                ofile.write(json.dumps(pd_result))
    else:
        tri_list_path = args.triplet
        tri_list = []
        with open(tri_list_path, 'r') as ifile:
            for line in ifile:
                tri_list.append(line.strip())
        result = pipeline(tri_list, word_model, topk)
        print(result)
    
        


