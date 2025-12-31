#coding='utf-8'
import os
from importlib import reload
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
from gensim import corpora,similarities,models
from gensim.models import LdaModel
from gensim.corpora import Dictionary
#from ldamattle import LdaMallet#导入mallet
import pyLDAvis.gensim
import math
import jieba.posseg as pseg
import matplotlib.pyplot as plt
from gensim.models import CoherenceModel
import time
import datetime

def infile(fliepath):
    #输入分词好的TXT，返回train
    print(f"[DEBUG] 开始读取文件: {fliepath}")
    start_time = time.time()
    
    train = []
    line_count = 0
    word_count = 0
    
    fp = open(fliepath,'r',encoding='utf8')
    for line in fp:
        new_line=[]
        if len(line)>1:
            line = line.strip().split(' ')
            for w in line:
                w.encode(encoding='utf-8')
                new_line.append(w)
                word_count += 1
        if len(new_line)>1:
            train.append(new_line)
            line_count += 1
            
            # 每处理100行输出一次进度
            if line_count % 100 == 0:
                print(f"[DEBUG] 已处理 {line_count} 行，{word_count} 个词语")
    
    fp.close()
    
    end_time = time.time()
    print(f"[DEBUG] 文件读取完成，共处理 {line_count} 行文档，{word_count} 个词语")
    print(f"[DEBUG] 读取耗时: {end_time - start_time:.2f} 秒")
    print(f"[DEBUG] 训练数据样本数: {len(train)}")
    if len(train) > 0:
        print(f"[DEBUG] 第一条样本长度: {len(train[0])}")
        print(f"[DEBUG] 第一条样本预览: {train[0][:10]}...")
    
    return train

def deal(train):
    #输入train，输出词典,texts和向量
    print(f"[DEBUG] 开始处理训练数据，样本数: {len(train)}")
    start_time = time.time()
    
    # 创建词典
    print("[DEBUG] 创建词典...")
    id2word = corpora.Dictionary(train)     # Create Dictionary
    print(f"[DEBUG] 词典大小: {len(id2word)}")
    
    texts = train                           # Create Corpus
    
    # 创建词袋模型
    print("[DEBUG] 创建词袋模型...")
    corpus = [id2word.doc2bow(text) for text in texts]   # Term Document Frequency
    
    # 统计语料信息
    total_words = sum(len(doc) for doc in corpus)
    avg_words_per_doc = total_words / len(corpus) if len(corpus) > 0 else 0
    print(f"[DEBUG] 语料统计 - 文档数: {len(corpus)}, 总词数: {total_words}, 平均每文档词数: {avg_words_per_doc:.2f}")

    #使用tfidf
    print("[DEBUG] 应用TF-IDF转换...")
    tfidf = models.TfidfModel(corpus)
    corpus = tfidf[corpus]

    # 创建必要的目录
    os.makedirs('tmp', exist_ok=True)
    
    # 保存词典和语料
    print("[DEBUG] 保存词典和语料到tmp目录...")
    id2word.save('tmp/deerwester.dict') #保存词典
    corpora.MmCorpus.serialize('tmp/deerwester.mm', corpus)#保存corpus
    
    end_time = time.time()
    print(f"[DEBUG] 数据处理完成，耗时: {end_time - start_time:.2f} 秒")

    return id2word,texts,corpus

'''
# Build LDA model
lda_model = LdaModel(corpus=corpus,
                                           id2word=id2word,
                                           num_topics=10, 
                                           random_state=100,
                                           update_every=1,
                                           chunksize=100,
                                           passes=10,
                                           alpha='auto',
                                           per_word_topics=True)
# Print the Keyword in the 10 topics
print(lda_model.print_topics())
doc_lda = lda_model[corpus]
'''

def run(corpus_1,id2word_1,num,texts):
    #标准LDA算法
    print(f"[DEBUG] 开始训练LDA模型，主题数: {num}")
    print(f"[DEBUG] 模型参数 - passes: 60, alpha: {50/num:.2f}, eta: 0.01, random_state: 42")
    start_time = time.time()
    
    lda_model = LdaModel(corpus=corpus_1, 
                         id2word=id2word_1,
                        num_topics=num,
                       passes=60,
                       alpha=(50/num),
                       eta=0.01,
                       random_state=42)
    
    end_time = time.time()
    print(f"[DEBUG] LDA模型训练完成，耗时: {end_time - start_time:.2f} 秒")
    
    # 输出主题
    print("[DEBUG] 主题分布预览:")
    topic_list = lda_model.print_topics(num_words=5)  # 每个主题显示前5个词
    for i, topic in enumerate(topic_list):
        print(f"  主题 {i}: {topic}")
    
    # 困惑度
    print("[DEBUG] 计算困惑度...")
    perplex=lda_model.log_perplexity(corpus_1)  # a measure of how good the model is. lower the better.
    print(f"[DEBUG] 困惑度: {perplex}")
    
    # 一致性
    print("[DEBUG] 计算一致性指数...")
    coherence_model_lda = CoherenceModel(model=lda_model, texts=texts, dictionary=id2word_1, coherence='c_v')
    coherence_lda = coherence_model_lda.get_coherence()
    print(f"[DEBUG] 一致性指数: {coherence_lda}")
    
    print(f"[DEBUG] 模型评估完成 - 困惑度: {perplex}, 一致性: {coherence_lda}")
    
    return lda_model,coherence_lda,perplex

def detailed_statistics(train, id2word, corpus):
    """提供详细的数据统计信息"""
    print("\n[详细统计]")
    
    # 文档统计
    print("1. 文档统计:")
    print(f"   - 文档总数: {len(train)}")
    
    # 词汇统计
    print("2. 词汇统计:")
    print(f"   - 词典大小: {len(id2word)}")
    
    # 文档长度统计
    doc_lengths = [len(doc) for doc in train]
    print(f"   - 平均文档长度: {sum(doc_lengths) / len(doc_lengths):.2f} 词")
    print(f"   - 最短文档: {min(doc_lengths)} 词")
    print(f"   - 最长文档: {max(doc_lengths)} 词")
    
    # 词频统计
    word_freq = {}
    for doc in train:
        for word in doc:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    print(f"3. 高频词汇 (前10):")
    for i, (word, freq) in enumerate(sorted_words[:10]):
        print(f"   {i+1:2d}. {word}: {freq} 次")
    
    # 稀疏度统计
    total_possible_terms = len(id2word) * len(corpus)
    actual_terms = sum(len(doc) for doc in corpus)
    sparsity = 1 - (actual_terms / total_possible_terms)
    print(f"4. 语料稀疏度: {sparsity:.4f}")
    print(f"   - 总可能词项: {total_possible_terms}")
    print(f"   - 实际词项: {actual_terms}")

def save_visual(lda,corpus,id2word,name):
    #保存为HTML
    print(f"[DEBUG] 开始生成可视化文件: {name}.html")
    start_time = time.time()
    
    d=pyLDAvis.gensim.prepare(lda, corpus, id2word)
    pyLDAvis.save_html(d, name+'.html')#可视化
    
    end_time = time.time()
    print(f"[DEBUG] 可视化文件生成完成，耗时: {end_time - start_time:.2f} 秒")
    print(f"[DEBUG] 可视化文件已保存为: {name}.html")

def mallet(corpus_1,id2word_1,num,texts_1):
    #Mallet 版本的 LDA 算法
    print(f"[DEBUG] 开始训练Mallet LDA模型，主题数: {num}")
    print("[DEBUG] 设置Mallet路径...")
    os.environ.update({'MALLET_HOME':r'E:/mallet/mallet-2.0.8/'})
    mallet_path = 'E:\\mallet\\mallet-2.0.8\\bin\\mallet.bat' #路径
    print(f"[DEBUG] Mallet路径: {mallet_path}")
    
    start_time = time.time()
    ldamallet = LdaMallet(mallet_path, corpus=corpus_1, num_topics=num, id2word=id2word_1)
    end_time = time.time()
    
    print(f"[DEBUG] Mallet LDA模型训练完成，耗时: {end_time - start_time:.2f} 秒")
    
    # Show Topics
    print("[DEBUG] Mallet主题分布预览:")
    topic_list = ldamallet.show_topics(formatted=False, num_words=5)
    for i, topic in enumerate(topic_list):
        print(f"  主题 {i}: {topic}")

    # Compute Coherence Score
    print("[DEBUG] 计算Mallet一致性指数...")
    coherence_model_ldamallet = CoherenceModel(model=ldamallet, texts=texts_1, dictionary=id2word_1, coherence='c_v')
    coherence_ldamallet = coherence_model_ldamallet.get_coherence()
    print(f"[DEBUG] Mallet一致性指数: {coherence_ldamallet}")
    
    return ldamallet,coherence_ldamallet


if __name__ == '__main__':
    print("=" * 60)
    print("[INFO] LDA主题模型分析程序启动")
    print(f"[INFO] 开始时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    total_start_time = time.time()
    
    # 1. 读取数据
    print("\n[阶段1] 数据读取")
    train=infile('./qx_分词结果.txt')
    
    # 2. 数据处理
    print("\n[阶段2] 数据处理")
    id2word,texts,corpus=deal(train)
    
    # 2.5 详细统计信息
    print("\n[阶段2.5] 数据统计分析")
    detailed_statistics(train, id2word, corpus)
    
    # 3. 训练LDA模型
    print("\n[阶段3] LDA模型训练")
    lda_model,coherence_lda,perplex=run(corpus,id2word,6,texts)
    
    # 4. 保存主题结果
    print("\n[阶段4] 保存主题结果")
    topic_list = lda_model.print_topics()
    f=open('qx_主题.txt','w',encoding='utf-8')
    for t in topic_list:
        f.write(' '.join(str(s) for s in t) + '\n')
    f.close()
    print(f"[DEBUG] 主题结果已保存到: qx_主题.txt")
    
    # 5. 生成可视化
    print("\n[阶段5] 生成可视化")
    save_visual(lda_model,corpus,id2word,'qx_主题')
    
    total_end_time = time.time()
    
    print("\n" + "=" * 60)
    print("[INFO] LDA主题模型分析完成")
    print(f"[INFO] 总耗时: {total_end_time - total_start_time:.2f} 秒")
    print(f"[INFO] 完成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 输出最终结果摘要
    print("\n[结果摘要]")
    print(f"- 主题数量: 6")
    print(f"- 一致性指数: {coherence_lda:.4f}")
    print(f"- 困惑度: {perplex:.4f}")
    print(f"- 生成文件:")
    print(f"  - qx_主题.txt (主题分布)")
    print(f"  - qx_主题.html (可视化)")
    print(f"  - tmp/deerwester.dict (词典)")
    print(f"  - tmp/deerwester.mm (语料)")
