import ast

def extract_snippets(code):
    tree = ast.parse(code)
    snippets = []

    class SnippetExtractor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            snippets.append(ast.unparse(node))

        def visit_ClassDef(self, node):
            snippets.append(ast.unparse(node))

    visitor = SnippetExtractor()
    visitor.visit(tree)
    return snippets

# Example usage
code = """
import os
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import chromadb
from PIL import Image
from termcolor import colored

import autogen
from autogen import Agent, AssistantAgent, ConversableAgent, UserProxyAgent
from autogen.agentchat.contrib.img_utils import _to_pil, get_image_data
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.code_utils import DEFAULT_MODEL, UNKNOWN, content_str, execute_code, extract_code, infer_lang


import autogen
from autogen import AssistantAgent, Agent, UserProxyAgent, ConversableAgent
from autogen.code_utils import DEFAULT_MODEL, UNKNOWN, content_str, execute_code, extract_code, infer_lang
config_list_gemini = autogen.config_list_from_json(
    "OAF_CONFIG_LIST.json",
    filter_dict={
        "model": ["gemini-pro"],
    },
)
assistant = AssistantAgent(
    "assistant", llm_config={"config_list": config_list_gemini, "seed": 42}, max_consecutive_auto_reply=10
)
user_proxy = UserProxyAgent(
    "user_proxy",
    code_execution_config={"work_dir": "coding", "use_docker": False},
    human_input_mode="NEVER",
    is_termination_msg=lambda x: content_str(x.get("content")).find("TERMINATE") >= 0,
)
"""

snippets = extract_snippets(code)
print(snippets)