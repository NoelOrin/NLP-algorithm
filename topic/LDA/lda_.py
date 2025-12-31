import warnings
import time
import logging
from datetime import datetime

# 抑制所有警告
warnings.filterwarnings("ignore")

# 特别抑制pkg_resources弃用警告
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lda_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_execution_time(func):
    """装饰器：记录函数执行时间"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"开始执行函数: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"函数 {func.__name__} 执行完成，耗时: {execution_time:.4f}秒")
            return result
        except Exception as e:
            logger.error(f"函数 {func.__name__} 执行出错: {str(e)}")
            raise
    
    return wrapper

@log_execution_time
def infile(fliepath):
    #输入分词好的TXT，返回train
    logger.info(f"开始读取文件: {fliepath}")
    
    train = []
    line_count = 0
    word_count = 0
    
    try:
        with open(fliepath,'r',encoding='utf8') as fp:
            for line_num, line in enumerate(fp, 1):
                line_count += 1
                new_line=[]
                
                if len(line)>1:
                    line = line.strip().split(' ')
                    for w in line:
                        try:
                            w.encode(encoding='utf-8')
                            new_line.append(w)
                            word_count += 1
                        except UnicodeEncodeError as e:
                            logger.warning(f"第{line_num}行包含非UTF-8字符: {w}")
                            continue
                
                if len(new_line)>1:
                    train.append(new_line)
                    if len(train) % 1000 == 0:  # 每1000行记录一次进度
                        logger.info(f"已处理 {len(train)} 行，当前行: {line_num}")
    
    except FileNotFoundError:
        logger.error(f"文件不存在: {fliepath}")
        raise
    except Exception as e:
        logger.error(f"读取文件时出错: {str(e)}")
        raise
    
    logger.info(f"文件读取完成: 总行数={line_count}, 有效行数={len(train)}, 总词数={word_count}")
    return train

@log_execution_time
def deal(train):
    #输入train，输出词典,texts和向量
    logger.info(f"开始处理文本数据: 文档数量={len(train)}")
    
    from gensim import corpora, models
    
    # 创建词典
    logger.info("开始创建词典...")
    id2word = corpora.Dictionary(train)
    logger.info(f"词典创建完成: 词汇数量={len(id2word)}")
    
    texts = train
    
    # 创建语料库
    logger.info("开始创建语料库向量...")
    corpus = [id2word.doc2bow(text) for text in texts]
    logger.info(f"语料库创建完成: 文档向量数量={len(corpus)}")

    # 使用tfidf
    logger.info("开始应用TF-IDF转换...")
    tfidf = models.TfidfModel(corpus)
    corpus = tfidf[corpus]
    logger.info("TF-IDF转换完成")

    # 保存模型文件
    logger.info("开始保存词典和语料库...")
    id2word.save('tmp/deerwester.dict')
    corpora.MmCorpus.serialize('tmp/deerwester.mm', corpus)
    logger.info("模型文件保存完成")

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

@log_execution_time
def run(corpus_1,id2word_1,num,texts):
    #标准LDA算法
    logger.info(f"开始训练LDA模型: 主题数={num}, 语料大小={len(corpus_1)}")
    
    from gensim.models import LdaModel, CoherenceModel
    
    # 训练LDA模型
    logger.info("开始LDA模型训练...")
    lda_model = LdaModel(corpus=corpus_1,
                         id2word=id2word_1,
                        num_topics=num,
                       passes=60,
                       alpha=(50/num),
                       eta=0.01,
                       random_state=42)
    
    logger.info("LDA模型训练完成")
    
    # 计算困惑度
    logger.info("开始计算困惑度...")
    perplex=lda_model.log_perplexity(corpus_1)
    logger.info(f"困惑度计算完成: {perplex:.4f}")
    
    # 计算一致性
    logger.info("开始计算一致性指数...")
    coherence_model_lda = CoherenceModel(model=lda_model, texts=texts, dictionary=id2word_1, coherence='c_v')
    coherence_lda = coherence_model_lda.get_coherence()
    logger.info(f"一致性指数计算完成: {coherence_lda:.4f}")
    
    # 输出主题信息
    logger.info("模型训练完成，开始输出主题信息...")
    topic_list = lda_model.print_topics()
    for i, topic in enumerate(topic_list):
        logger.info(f"主题 {i+1}: {topic[1][:100]}...")
    
    logger.info(f"LDA模型训练完成 - 主题数: {num}, 困惑度: {perplex:.4f}, 一致性: {coherence_lda:.4f}")
    return lda_model,coherence_lda,perplex

@log_execution_time
def save_visual(lda,corpus,id2word,name):
    #保存为HTML
    logger.info(f"开始生成可视化文件: {name}.html")
    
    import pyLDAvis.gensim
    
    try:
        logger.info("开始准备可视化数据...")
        d=pyLDAvis.gensim.prepare(lda, corpus, id2word)
        logger.info("可视化数据准备完成")
        
        logger.info("开始保存HTML文件...")
        pyLDAvis.save_html(d, name+'.html')
        logger.info(f"可视化文件保存完成: {name}.html")
        
    except Exception as e:
        logger.error(f"生成可视化文件时出错: {str(e)}")
        raise


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("LDA主题模型训练开始")
    logger.info("=" * 60)
    
    try:
        # 读取数据
        train=infile('qx_分词结果.txt')
        
        # 处理数据
        id2word,texts,corpus=deal(train)
        
        # 训练LDA模型
        lda_model, coherence, perplex = run(corpus,id2word,6,texts)
        
        # 保存主题结果
        logger.info("开始保存主题结果到文件...")
        topic_list = lda_model.print_topics()
        with open('qx_主题.txt','w',encoding='utf-8') as f:
            for i, topic in enumerate(topic_list):
                f.write(f"主题 {i+1}: {topic[1]}\n")
        logger.info("主题结果保存完成")
        
        # 生成可视化
        save_visual(lda_model,corpus,id2word,'qx_主题')
        
        # 输出最终结果
        logger.info("=" * 60)
        logger.info("LDA主题模型训练完成")
        logger.info(f"最终结果 - 主题数: 6, 困惑度: {perplex:.4f}, 一致性: {coherence:.4f}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"程序执行过程中出错: {str(e)}")
        raise
