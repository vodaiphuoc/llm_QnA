import json
from copy import deepcopy
import glob


for _file_path in glob.glob('crawl_service\crawl_results\[!temp_]*.json'):
    with open(_file_path, 'r',encoding= 'utf-8') as fp:
        json_crawl_data = json.load(fp)

    total_docs = []
    for post in json_crawl_data:
            
        for sub_head in post["sub_headings"]:
            new_sub_head = deepcopy(sub_head)

            new_sub_head['URL'] = post['URL']
            new_sub_head['Title'] = post['title'] if post.get('title') is not None else post['URL'].split('/')[-2]

            total_docs.append(new_sub_head)

    file_name = _file_path.split('\\')[-1]
    with open(f'original_data\crawl_data\\' + file_name,'w', encoding= 'utf-8') as f:
        json.dump(total_docs,f, indent= 4, ensure_ascii= False)