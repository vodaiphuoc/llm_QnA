"""
LLM tasks:
	- Give explaination to human language
	- Machine translation
"""
from typing import Union, List, Literal
# from src.data_models import ModelExplainResponse, ModelTranslateResponse, ModelContextTranslateResponse
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json


class Gemini_Inference(object):
	gemma_prompt = f"<start_of_turn>user\n{{input_prompt}}<end_of_turn><eos>\n"

	

	def __init__(self):
		load_dotenv()
		genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
		self.model = genai.GenerativeModel("gemini-1.5-flash")

	def __call__(self, prompt_data:str)->str:
		final_prompt = self.gemma_prompt.format(input_prompt = prompt_data)
		
		response = self.model.generate_content(
			contents = final_prompt, 
			# generation_config = genai.GenerationConfig(
			# 	response_mime_type=  "application/json",
			# 	response_schema = ModelExplainResponse)
			)
		return response.text
		# return self.post_processing(response.text, task = 'explain')

	# def post_processing(self,
	# 	model_response: str,
	# 	task: Literal['explain','translate'],
	# 	context_response: bool = False
	# 	)->Union[ModelExplainResponse, ModelTranslateResponse]:

	# 	reponse_dict = json.loads(model_response)
	# 	if task == 'explain':
	# 		return ModelExplainResponse(**reponse_dict)
	# 	else:
	# 		if context_response:
	# 			return ModelContextTranslateResponse(**reponse_dict)
	# 		else:
	# 			reponse_dict['describe'] = self.translate_sentence(reponse_dict['describe'], 
	# 																use_post_processing = True).transled_context_sentence
	# 			return ModelTranslateResponse(**reponse_dict)
