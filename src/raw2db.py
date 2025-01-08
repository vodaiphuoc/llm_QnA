import getpass
import os
import re
from uuid import uuid4
import glob

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredHTMLLoader


from src.data_models import Context, DocContext

class DataMerge(object):
    def __init__(self, 
                 gemini_model_url:str = "models/embedding-001", 
                 db_folder = 'db'
                 ) -> None:
        load_dotenv()
        embeddings_model = GoogleGenerativeAIEmbeddings(model=gemini_model_url, 
                                                             task_type="retrieval_document")
        
        self.db = Chroma(collection_name='wiki', 
                    embedding_function=embeddings_model, 
                    persist_directory=db_folder
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
        self.db.add_documents(documents = total_Docs, ids = uuids)


    def load_crawl(self, data_dir:str = 'original_data\crawl_data'):
        files_path = list(glob.glob(pathname = data_dir+'\*.html'))
        total_docs = []
        for file_path in files_path:
            loader = UnstructuredHTMLLoader(file_path= file_path)
            data = loader.load()
            total_docs.extend(data)

        uuids = [str(uuid4()) for _ in range(len(total_docs))]
        self.db.add_documents(documents = total_docs, ids = uuids)
        
    def query(self, query_text: str, k:int)->Context:
        return Context([DocContext(content=content, sim_score= sim_score) 
                        for content, sim_score 
                        in self.db.similarity_search_with_score(query = query_text, k = k)
         ])

        