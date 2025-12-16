# Scientific-research-topic-automatic-recommendation
我们从chemRxiv、medRxiv、bioRxiv等预印本平台获取元数据，arXiv数据来自Kaggle；针对特定领域（CS.CL），在arXiv获取领域论文；同时，我们从OpenAlex平台获取补充元数据及并行文本，为知识图谱的构建提供引用关系数据。对外处理后的数据，我们基于NLP技术的RAKE算法从预印本的论文数据中提取初始概念，形成基础概念列表。在基础概念列表上，我们进行算法层面优化，结合领域特性筛选领域特定概念，最终通过人工和大模型双重校验，去除语法错误、非概念短语（如动词、连词）及冗余内容等，最终形成包含41409个概念的列表。
