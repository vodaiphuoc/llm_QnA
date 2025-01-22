import getpass
import os
import re
from uuid import uuid4
import glob
from tqdm import tqdm
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredHTMLLoader, JSONLoader
from tavily import TavilyClient

from src.data_models import Context, DocContext, Tavily_Reponse, Tavily_single_result

class RAG_tools(object):
    def __init__(self, 
                 gemini_model_url:str = "models/embedding-001", 
                 db_folder = 'db/vectordb'
                 ) -> None:
        load_dotenv()
        embeddings_model = GoogleGenerativeAIEmbeddings(model=gemini_model_url, 
                                                             task_type="retrieval_document")

        self.db_crawl = Chroma(collection_name='crawl_blogs',
                    embedding_function=embeddings_model, 
                    persist_directory=db_folder
                    )
        
        self.tavily_search = TavilyClient(api_key= os.environ["TAVILY_KEY"])

    @staticmethod
    def _metadata_func(record: dict, metadata: dict) -> dict:
        metadata["Title"] = record.get("Title")
        metadata["heading"] = record.get("heading")
        return metadata


    def load_crawl(self, data_dir:str = 'original_data\crawl_data'):
        """Json files are crawled from crawl_service"""
        files_path = list(glob.glob(pathname = data_dir+'\*.json'))
        total_docs = []
        for file_path in files_path:
            loader = JSONLoader(file_path= file_path, 
                                content_key = 'body_content',
                                jq_schema='.[]',
                                metadata_func= RAG_tools._metadata_func)
            data = loader.load()
            total_docs.extend(data)
        
        # print(total_docs[0])
        
        uuids = [str(uuid4()) for _ in range(len(total_docs))]
        
        batch_size = 150
        for i in tqdm(range(0, len(total_docs), batch_size)):
            self.db_crawl.add_documents(documents = total_docs[i: i+batch_size], 
                                        ids = uuids[i: i+batch_size])
        
    def search_facts(self, query_search:str)->str:
        """
        Function to perform searching facts, definitions or location, etc ... .
        Args:
            - query_search (str): input query for searching information
        Returns:
            - a formated string described as below
                - `query_search`: contains origial query search
                - `results`: a string search results with many results, each 
        contains `Title`, `Reference`, `Content`, `Relevance score`
        """
        response = self.tavily_search.search(query= query_search)
        search_results = response['results']
        return Tavily_Reponse(
            query_seach = query_search,
            reponses = [    Tavily_single_result(ith = ith+1, **_result) 
                            for ith, _result in enumerate(search_results)
                        ]
        ).to_string

    def find_blogs(self, query_search: str, k:int = 15)->str:
        """
        Function to perform searching in Chroma vector database for collection `blogs` which
        contains data crawl from travel blogs.
        Args:
            - query_search (str): query to relevant travelling blogs
            - k (int): Number of retrieval documents. Defaul is 15
        Returns:
            - a formated string described as below
                - `query_search`: contains origial query search
                - `results`: a string search results with many results, each contains content and 
        similarity score to input `query_text`.Lower score represents more similarity.
        """
        return Context(
            query_seach = query_search,
            contexts=[DocContext(content = document.page_content, 
                                sim_score = sim_score,
                                ith = ith+1) 
                    for ith, (document, sim_score)
                    in enumerate(self.db_crawl.similarity_search_with_score(query = query_search, k = int(k)))
        ]).to_string
