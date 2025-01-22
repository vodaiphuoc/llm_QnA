from pydantic.dataclasses import dataclass
from pydantic import computed_field
from typing import List, Dict, Any


########### for Chroma DB
@dataclass
class DocContext:
    ith:int
    content:str
    sim_score:float

    @computed_field
    @property
    def to_string(self)->str:
        return f"""
{{
    Content: {self.content}
    Relevance score: {self.sim_score}
}}
"""

@dataclass
class Context:
    query_seach: str
    contexts: List[DocContext]

    @computed_field
    @property
    def to_string(self)->str:
        results_str = "".join([_res.to_string for _res in self.contexts])

        return f"""
search blogs results:
{results_str}
"""    


########### for Tavily search
@dataclass
class Tavily_single_result:
    ith: int
    title: str
    url: str
    content: str
    score: float
    raw_content = None

    @computed_field
    @property
    def to_string(self)->str:
        return f"""
    Title: {self.title}
    Reference: {self.url}
    Content: {self.content}
    Relevance score: {self.score}
"""

@dataclass
class Tavily_Reponse:
    query_seach: str
    reponses: List[Tavily_single_result]

    @computed_field
    @property
    def to_string(self)->str:
        results_str = "".join([_res.to_string for _res in self.reponses])

        return f"""
search results:
{results_str}
"""


########### for Tools
@dataclass
class Tool_Description:
    tool_name: str
    signatures: Dict[str,Any]
    description: str

    @computed_field
    @property
    def to_string(self)->str:
        return f"""
    {{
        Tool name: {self.tool_name}
        Tool signatures: {self.signatures}
        Tool description:
        {self.description}
    }}
"""

@dataclass
class Tool_List_Description:
    tool_list: List[Tool_Description]

    @computed_field
    @property
    def to_string(self)->str:
        tool_list_as_str = ','.join([tool.to_string for tool in self.tool_list])
        return f"""
[
    {tool_list_as_str}
]"""