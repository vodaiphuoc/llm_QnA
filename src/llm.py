from typing import Union, List, Literal, Dict, Optional
import google.generativeai as genai
from google.generativeai.types import content_types

from dotenv import load_dotenv
import os
import json
from src.search import SearchEngine
from collections.abc import Iterable
from dataclasses import dataclass

@dataclass
class SingleFinalResponse:
    task_id: str
    question: str
    answer:str

def tool_config_from_mode(mode: str, fns: Iterable[str] = ()):
	return content_types.to_tool_config(
		{"function_calling_config": {"mode": mode, "allowed_function_names": fns}}
	)

class Agent(object):
    intent_prompt = f"""<start_of_turn>user\n
    Given the below question and perform the following tasks:
    - Detect if the original query of user can be decomposited into many queries
    - For each sub query (if exist) ,use provided tools if you need to get more external information else answer directly
    {{input_prompt}}
    <end_of_turn><eos>\n"""

    single_trajectory = f"""
**Task {{ith}}
    Question: {{question}}
    Action: {{action}}
    Action Input: {{action_input}}
    Observation: {{observation}}
"""
    final_answer_prompt = f"""
<start_of_turn>user\n
    Given below task, you have give answer for each task
    Each task includes question, action and observation as context to give final answer
    {{input_trajectory}}
<end_of_turn><eos>\n
"""

    def __init__(self):
        self.search_engine = SearchEngine()
        load_dotenv()
        genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

        self.func_list = [self.search_engine.search]
        self.func_name_list = ['search']
        self.func_mapp = {name: obj 
                          for name, obj in 
                          zip(self.func_name_list, self.func_list)
                          }

        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def post_execute(self, parts: List[genai.protos.Part])->List[Dict[str,str]]:
        """
        Post processing for function calling, invoke selected tools
        """
        total_search_results = []
        for part in parts:
            function_dict = type(part).to_dict(part)['function_call']
            search_result = self.func_mapp[function_dict['name']](**function_dict['args'])
            total_search_results.append({
                'question': search_result['query'],
                'action': function_dict['name'],
                'action_input': function_dict['args'],
                'observation': search_result['result']
            })
        return total_search_results
    
    def final_processing(self, reponse: List[Dict[str,str]])->str:
        return "\n".join([ele['answer'] for ele in reponse])

    def __call__(self, prompt_data:str)->List[str]:
        # step 0
        init_prompt = self.intent_prompt.format(input_prompt = prompt_data)

        # step 1: 
        response = self.model.generate_content(contents = init_prompt,
                                               tools = self.func_list,
                                               tool_config = tool_config_from_mode(
                                                    mode= "any", 
                                                    fns = self.func_name_list
                                               )
        )
        
        # step 2:
        contexts = self.post_execute(response.parts)

        # step 3:
        final_prompt = "\n".join([self.single_trajectory.format(ith = ith, **context) 
                                 for ith, context in enumerate(contexts)
                                 ])
        
        final_prompt = self.final_answer_prompt.format(input_trajectory = final_prompt)

        response = self.model.generate_content(
            contents = final_prompt,
            generation_config={"response_mime_type": "application/json",
                               "response_schema": list[SingleFinalResponse]}
        )
        # step 4
        return self.final_processing(json.loads(response.text))