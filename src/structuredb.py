from pydantic import TypeAdapter

import sqlite3
import json
from typing import List, Tuple, Literal, Union, Dict
import re

class ChatHistoryDB(object):
    """
    Database for storage files content
    """
    def __init__(self, db_url = 'db/history/chat_history.db') -> None:
        try:
            self.connection = sqlite3.connect(db_url)
            
        except sqlite3.Error as error:
            print(f"Cannot connect to {db_url} db, ", error)

        try:
            with self.connection:
                create_prompt = """
CREATE TABLE chat_history (id INTEGER PRIMARY KEY, Topic TEXT, Role TEXT, Parts TEXT);
""" 
                self.connection.execute(create_prompt)
        except sqlite3.Error as error:
            print('Cannot create table', error)

    def insert_new_turns(self,
                    topic: str,
                    new_msgs: List[Dict[str, str]]
                    )->None:
        """
        Insert new user and model reponse into db
        Args:
            - topic (str): topic of current conversation
            - new_msgs (List[Dict[str, str]]): new data of conversation
        
        Example:
            - topic = 'Hoi An'
            - new_msgs = [
                {"role": "user", "parts": "Hello"},
                {"role": "model", "parts": "Great to meet you"}
            ]
        """
        prepare_data = [(topic, msg['role'], msg['parts']) for msg in new_msgs]
        try:
            with self.connection:
                insert_prompt = """
                    INSERT INTO chat_history (SearchFileUrl, RawContent, RenderContent) VALUES (?,?,?);
                """ 
                self.connection.executemany(insert_prompt, prepare_data)

        except Exception as error:
            print(f"Cannot peform insert many files, error: ", error)

    def close(self):
        self.connection.close()

    def get_chat_history(self, topic:str)->str:
        try:
            with self.connection:
                query_prompt = f"""SELECT {target_col} FROM user_files WHERE SearchFileUrl LIKE '%{url}';"""
                records = self.connection.execute(query_prompt).fetchall()
                return records[0][0] if self.db_type == 'implement' else records[0]
        
        except Exception as error:
            print(f"Cannot peform select file {url} error: ", error)        
