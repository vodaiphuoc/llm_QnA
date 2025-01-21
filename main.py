from src.raw2db import DataMerge


data_hander = DataMerge()
# data_hander.load_wiki('original_data/wiki/wikidata5m_corpus.txt')
data_hander.load_crawl(data_dir= 'original_data\crawl_data')

_result = DataMerge().query_crawl_data('Phố cổ Hà Nội')
print(_result)