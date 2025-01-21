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


from src.data_models import Context, DocContext

class DataMerge(object):
    def __init__(self, 
                 gemini_model_url:str = "models/embedding-001", 
                 db_folder = 'db'
                 ) -> None:
        load_dotenv()
        embeddings_model = GoogleGenerativeAIEmbeddings(model=gemini_model_url, 
                                                             task_type="retrieval_document")
        
        self.db_wiki = Chroma(collection_name='wiki',
                    embedding_function=embeddings_model,
                    persist_directory=db_folder+'/wiki'
                    )

        self.db_crawl = Chroma(collection_name='crawl', 
                    embedding_function=embeddings_model, 
                    persist_directory=db_folder+'/crawl'
                    )

    def load_wiki(self, file_path:str):
        """load original file to vector DB
        support format: .txt file
        """

        total_Docs = []
        with open(file_path, mode= 'r', encoding= 'utf-8') as fp:
            for ith, line in enumerate(fp.readlines()):
                entity_id = re.search(r'^Q\d+\s', line).group(0)

                document = Document(
                    page_content = line.replace(entity_id,''),
                    metadata={"entity_id": entity_id},
                    id = ith+1
                )
                total_Docs.append(document)

        uuids = [str(uuid4()) for _ in range(len(total_Docs))]
        self.db_wiki.add_documents(documents = total_Docs, ids = uuids)

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
                                metadata_func= DataMerge._metadata_func)
            data = loader.load()
            total_docs.extend(data)
        
        # print(total_docs[0])
        
        uuids = [str(uuid4()) for _ in range(len(total_docs))]
        
        batch_size = 150
        for i in tqdm(range(0, len(total_docs), batch_size)):
            self.db_crawl.add_documents(documents = total_docs[i: i+batch_size], 
                                        ids = uuids[i: i+batch_size])
        
    def query_wiki_corpus(self, query_text: str, k:int = 5)->Context:
        """
        Function to perform searching in Chroma vector database for collection `wiki` which
        contains data from wikidata5m dataset.
        Args:
            - query_text (str): query to search in the collection
            - k (int): Number of retrieval documents. Defaul is 5
        Returns:
            - Context: an instance of `Context` dataclass which contains list of `DocContext`.
            Each `DocContext` containts content and similarity score to input `query_text`.Lower 
            score represents more similarity
        """
        return Context(contexts=[DocContext(content=document.page_content, 
                                                sim_score= sim_score) 
                                    for document, sim_score 
                                    in self.db_wiki.similarity_search_with_score(query = query_text, k = k)
        ])

    def query_crawl_data(self, query_text: str, k:int = 15)->Context:
        """
        Function to perform searching in Chroma vector database for collection `crawl` which
        contains data crawl from travel blogs.
        Args:
            - query_text (str): query to search in the collection
            - k (int): Number of retrieval documents. Defaul is 15
        Returns:
            - Context: an instance of `Context` dataclass which contains list of `DocContext`.
            Each `DocContext` containts content and similarity score to input `query_text`.Lower 
            score represents more similarity
        """
        return Context(contexts=[DocContext(content = document.page_content, 
                                            sim_score = sim_score) 
                                    for document, sim_score 
                                    in self.db_crawl.similarity_search_with_score(query = query_text, k = k)
        ])