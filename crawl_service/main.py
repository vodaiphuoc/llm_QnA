import requests
import bs4
import re
from typing import Union, List, Literal, Dict
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from dataclasses import dataclass
import time
import typing
from tqdm import tqdm

@dataclass
class HeadingContent:
    heading: str
    body_content:str
    image_link: str

@dataclass
class ScrapesResponse:
    Input: int
    URL: str
    title:str
    sub_headings: List[HeadingContent]

@dataclass
class BatchResponse:
    batch_response: List[ScrapesResponse]

class Summary_Agent(object):
    gemma_prompt = f"<start_of_turn>user\n{{input_prompt}}<end_of_turn><eos>\n"

    example = """
{
    "Input": 1,
    "sub_headings": [
            {
                "body_content": "Theo tờ báo Daily Mail của Anh vào tháng 4 năm 2024, cảnh quan Ninh Bình đứng thứ 4 trong 10 kỳ quan thế giới, với những đỉnh đá vôi kéo dài không kém phần ấn tượng so với điểm đến nổi tiếng của Vịnh Hạ Long, nhưng nhìn chung nơi đây vẫn chưa quá đông đúc.",
                "heading": "Tổng quan Ninh Bình",
                "image_link": "https://www.dulichvtv.com/wp-content/uploads/2024/04/Tour-Ninh-Binh-Bai-Dinh-Trang-An.jpg"
            },
            {
                "body_content": "Địa danh này chưa bị thương mại hóa nhiều, nên vẫn còn \"ít đám đông\". Đặc biệt, Ninh Bình “sở hữu” Quần thể Danh thắng Tràng An - Di sản văn hóa và thiên nhiên thế giới. Đây là Di sản thế giới kép đầu tiên và duy nhất ở khu vực Đông Nam Á. Trải rộng trên 12.000 ha, đây là nơi văn hóa giao thoa với sự kỳ diệu, bí ẩn và hùng vĩ của tự nhiên gồm khu di tích lịch sử văn hóa cố đô Hoa Lư, khu danh thắng Tràng An - Tam Cốc - Bích Động và rừng nguyên sinh đặc dụng Hoa Lư… Trong đó nổi bật là khu danh thắng Tràng An nằm ở vị trí trung tâm Quần thể. Với phong cảnh được nhận xét \"đẹp như tranh vẽ\", cùng nhiều địa điểm du lịch tâm linh nổi tiếng, lễ hội độc đáo, đặc sản hấp dẫn, Tràng An đang trở thành một trong những địa điểm du lịch đáng tham quan nhất của Việt Nam.",
                "heading": "Quần thể Danh thắng Tràng An",
                "image_link": "https://www.dulichvtv.com/wp-content/uploads/2024/04/Le-hoi-Trang-An-Ninh-Binh.jpg"
            }
    ],
    "title": "Ninh Bình Thuộc Top 10 Kì Quan Thế Giới \"Không Đông Đúc\"",
    "URL": "https://www.dulichvtv.com/ninh-binh-thuoc-top-10-ki-quan-the-gioi-khong-dong-duc/"
}
"""
    example_error = """
{
    "Input": 3,
    "sub_headings": [
            {
                "body_content": "Theo tờ báo Daily Mail của Anh vào tháng 4 năm 2024, cảnh quan Ninh Bình đứng thứ 4 trong 10 kỳ quan thế giới, với những đỉnh đá vôi kéo dài không kém phần ấn tượng so với điểm đến nổi tiếng của Vịnh Hạ Long, nhưng nhìn chung nơi đây vẫn chưa quá đông đúc.",
                "heading": "Tổng quan Ninh Bình",
                "image_link": "https://www.dulichvtv.com/wp-content/uploads/2024/04/Tour-Ninh-Binh-Bai-Dinh-Trang-An.jpg"
            },
            {
                "body_content": "",
                "heading": "",
                "image_link": "https://www.dulichvtv.com/wp-content/uploads/2024/04/Le-hoi-Trang-An-Ninh-Binh.jpg"
            }
    ],
    "title": "Ninh Bình Thuộc Top 10 Kì Quan Thế Giới \"Không Đông Đúc\"",
    "URL": "https://www.dulichvtv.com/ninh-binh-thuoc-top-10-ki-quan-the-gioi-khong-dong-duc/"
}
"""
    
    base_prompt = f"""
- Given the page content of html file and its url, please summarize content of this page includes title, each location or 
destination in sub heading and image source (if no image, place None)
- Remove any irrelevant content
- Please reponse in batch data `BatchResponse` for many inputs where each data input has **Input, **URL and **Page content
- If you cannot find information of `heading`, `body_content` or `image_link`, left the fields an empty string
- Example of single output format
{{example}}
- Example of single output format when you cannot find formation
{{example_error}}

- Please ingore the URL, just put it in output

Now give output with below data:
{{batch_data}}
"""
    def __init__(self):
        load_dotenv()
        genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
        self.model = genai.GenerativeModel("gemini-1.5-flash", system_instruction= "Your are professional content summarization")

        self.limit_counts = int(0.9*10**6)

    def batch_inference(method_func):
        
        def wrapper(self, batch_data: List[Dict[str,str]]):
            batch_prompt = "\n".join([f"**Input {ith+1}\n**URL\n{each_data['url']}\n**Page content\n{each_data['content']}" 
                        for ith, each_data in enumerate(batch_data)])

            num_tokens = int(self.model.count_tokens(batch_prompt).total_tokens)
            if num_tokens > self.limit_counts:
                batch_size = 2
                
                total_reponse_list = []

                ids_iter = list(range(0,len(batch_data),batch_size))

                for ith, i in tqdm(enumerate(ids_iter), total= len(ids_iter)):
                    reponse_text = method_func(self, batch_data[i: i + batch_size], i)
                    if not reponse_text:
                        continue
                    else:
                        reponse_dict = json.loads(reponse_text)
                        # with open(f'crawl_service\\crawl_results\\temp_reponse_{ith+1}.json','w', encoding= 'utf-8') as f:
                        #     json.dump(reponse_dict,f, indent= 5, ensure_ascii= False)
                        total_reponse_list.extend(reponse_dict['batch_response'])
                        time.sleep(40)
                        print(f'done batch {ith+1}')
                
                return total_reponse_list

            else:
                reponse_text = method_func(self, batch_data, 0)
                try:
                    return json.loads(reponse_text)['batch_response']
                except Exception as err:
                    print(reponse_text)
                    return None

        return wrapper

    @batch_inference
    def __call__(self, batch_data: List[Dict[str,str]], batch_ids:int)->str:
        batch_prompt = "\n".join([f"**Input {batch_ids+ith+1}\n**URL\n{each_data['url']}\n**Page content\n{each_data['content']}\n" 
                        for ith, each_data in enumerate(batch_data)])
        
        num_token = int(self.model.count_tokens(batch_prompt).total_tokens)
        assert num_token < self.limit_counts

        final_prompt = self.gemma_prompt.format(input_prompt = self.base_prompt.format(example = self.example, 
                                                                                        example_error = self.example_error,
                                                                                        batch_data = batch_prompt)
                                                                                        )
        response = self.model.generate_content(
            contents = final_prompt, 
            generation_config = genai.GenerationConfig(
                # max_output_tokens= 8192,
            	response_mime_type=  "application/json",
            	response_schema = BatchResponse)
            )
        
        if all([cand.finish_reason.value == 1 for cand in  response.candidates]):
            return response.text
        else:
            return False

def get_page_content(url:str):
    time.sleep(10)
    response = requests.get(url=url)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.content, 'html.parser')
        # Remove tags
        for data in soup(['head','style', 'script','svg']):
            data.decompose()

        return str(soup)

    else:
        return None


def process_paginnation(origin_soup: bs4.BeautifulSoup):
    # find other pages (pagination)
    other_pages = [a_ele['href']
                    for a_ele
                    in origin_soup.find_all('a', attrs= {'class':'page-numbers'},href=True)
                    if 'http' in a_ele['href']
                    ]
    
    other_page_sub_links = []
    for page_origin in other_pages:
        response = requests.get(url=page_origin)
        assert response.status_code == 200
        other_page_soup = bs4.BeautifulSoup(response.content, 'html.parser')
        
        sub_links = [a_ele['href']
                         for a_ele
                         in other_page_soup.find_all('a', href=True)
                         if 'http' in a_ele['href'] and a_ele.parent.parent.name == 'article'
                         ]
        
        other_page_sub_links.extend(sub_links)
    return other_page_sub_links

def process_origin(origin_url:str = 'https://www.dulichvtv.com/cam-nang-du-lich'):
    response = requests.get(url=origin_url)

    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        if origin_url == 'https://www.dulichvtv.com/cam-nang-du-lich':
            sub_links = [a['href'] 
                         for a 
                         in soup.find_all('a', attrs= {'class': 'plain'}, href=True)
                         if 'http' in a['href']
                         ]
        elif origin_url == 'https://blog.ivivu.com/2024/12/':

            sub_links = [a_ele['href']
                         for a_ele
                         in soup.find_all('a', href=True)
                         if 'http' in a_ele['href'] and a_ele.parent.parent.name == 'article'
                         ]
            
            if len((_results:=process_paginnation(soup))) > 0:
                sub_links.extend(_results)
            return sub_links

        else:
            raise NotImplementedError

    else:
        return None

if __name__ == '__main__':
    
    #### support origin ####
    # origin_link = 'https://www.dulichvtv.com/cam-nang-du-lich'
    origin_link = 'https://blog.ivivu.com/2024/12/'

    #### processing ####
    # get link of blogs in origin
    # sub_links = process_origin(origin_url=origin_link)

    # # get content of each link
    # total_content = [
    #     {
    #         'content': get_page_content(url= link),
    #         'url': link
    #     }
    #     for link in sub_links
    # ]

    # origin_name = origin_link.split('/')[-1]
    # with open(f'crawl_service\\crawl_results\\temp_{origin_name}.json','w', encoding= 'utf-8') as f:
    #     json.dump(total_content,f, indent= 5, ensure_ascii= False)
    

    with open(f'crawl_service\\crawl_results\\temp_ivivu.json','r', encoding= 'utf-8') as fp:
        total_content =  json.load(fp)

    model = Summary_Agent()

    batch_reponse = model(total_content)

    # print(batch_reponse)

    origin_name = origin_link.split('/')[-1]
    with open(f'crawl_service\\crawl_results\\temp_ivivu.json','w', encoding= 'utf-8') as f:
        json.dump(batch_reponse,f, indent= 4, ensure_ascii= False)