from typing import Callable, List
import inspect
import json
from pydantic.dataclasses import dataclass
from pydantic.json import pydantic_encoder
from src.data_models import Tool_Description, Tool_List_Description
from src.vectordb import RAG_tools

########## format of Thought and Action answer
@dataclass
class Arg:
    key: str
    value: str

@dataclass
class Action_Type:
    function_name: str
    args: List[Arg]

@dataclass
class SingleFinalResponse:
    Thought: str
    Action: Action_Type


########## making of few-shot examples
EXAMPLE1_OUT = json.dumps(
        obj= SingleFinalResponse(
            Thought= 'I need to search information of Hoi An city', 
            Action = Action_Type(
                function_name= 'search_facts', 
                args = [Arg(key='query_search', value = 'where is Hoi An')]
            )
        ), 
        default=pydantic_encoder,
        indent= 4)

EXAMPLE2_OUT = json.dumps(
        obj= SingleFinalResponse(
            Thought= 'I need to find travelling blogs about Viet Nam', 
            Action = Action_Type(
                function_name= 'find_blogs', 
                args = [
                    Arg(key='query_search', value = 'popular location in Viet Name'),
                    Arg(key='k', value = '20')
                ]
            )
        ), 
        default=pydantic_encoder,
        indent= 4)

EXAMPLE3_OUT = json.dumps(
        obj= SingleFinalResponse(
            Thought= 'This question i can answer directly', 
            Action = Action_Type(
                function_name= 'give_direct_answer', 
                args = [
                    Arg(key="direct_answer", 
                        value = """Vietnam is located in Southeast Asia. It is situated on the eastern edge of 
                the Indochina Peninsula, bordering China to the north, Laos and Cambodia to the west, and the 
                South China Sea to the east"""
                    )
                ]
            )
        ), 
        default=pydantic_encoder,
        indent= 4)

class Agent_Base(RAG_tools):
    """
    Base class of Agent.
    Inheritance from `RAG_tools` to make 2 search functions
    as 2 methods of Agent.
    
    """
    def __init__(self, tools: List[Callable]):
        super().__init__()

        self.tool_list_desription = Tool_List_Description(
            tool_list = [Tool_Description(
                tool_name = tool.__name__,
                signatures = inspect.get_annotations(tool),
                description = inspect.getdoc(tool))
                for tool in tools]
        ).to_string

        self.func_name_to_func = {tool.__name__: tool for tool in tools}
    

    examples = f"""
    **Example 1**
    **Query**:
        Where is location of Hoi An city in Viet Nam
    **Output**
    {EXAMPLE1_OUT}

    **Example 2**
    **Query**:
        What are popular location to visit in Viet Nam
    **Output**
    {EXAMPLE2_OUT}

    **Example 3**
    **Query**:
        Where is Viet Nam
    **Output**
    {EXAMPLE3_OUT}
"""


