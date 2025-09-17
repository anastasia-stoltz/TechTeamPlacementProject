# dataset credits: https://www.kaggle.com/datasets/datacrux/barack-obama-twitterdata-from-20122019/code

import pandas as pd
import sqlite3

import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
import time
import json
import gradio as gr

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()

PATH_DATA = '/Users/stasia/Documents/TechTeam/Tweets-BarackObama.csv'

df = pd.read_csv(PATH_DATA)
#print(df.head(2))

#setting api keys
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
pine_key = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=pine_key)

client = OpenAI()

system_message = """
Pretend you are Barack Obama... Base your tone and phrasing on the language used in his verified tweets.
Respond only in ways consistent with Barack Obama’s public voice and persona.
"""

response = client.responses.create(
    model='gpt-5',
    input = system_message
)

df_clean = df.drop(['TweetImageUrl', 'Image'],axis=1)
#print(df_clean.head(2))

df["chunk_text"] = df["Tweet-text"]

def prepare_records(df: pd.DataFrame):
    return [
        {
            "id": str(row["index"]),
            "chunk_text": row["Tweet-text"]
        }
        for _, row in df.iterrows()
    ]

def upload_records(index, records, namespace='namespace', batch_size=96):
    index.upsert_records(namespace, records[:batch_size])
    time.sleep(10) #giving time for the index to process

def ensure_index(df: pd.DataFrame, index_name: str = 'quickstart-py', model_name: str = 'llama-text-embed-v2', namespace: str = 'namespace', batch_size: int = 96):
    if not pc.has_index(index_name):
        pc.create_index_for_model(
            name=index_name,
            cloud='aws',
            region='us-east-1',
            embed = {
                "model": model_name,
                "field_map": {"text": "chunk_text"}
            }
        )
        
        #Prepare records
        records = prepare_records(df)

        #Upload records
        upload_records(pc.Index(index_name), records, namespace=namespace, batch_size=batch_size)
        
    return pc.Index(index_name)


def search_query(index, query_text: str, namespace='namespace', top_k=10):
    return index.search(
        namespace=namespace,
        query={
            'top_k': top_k,
            'inputs': {'text': query_text}
        }
    )
    
def print_search_results(results):
    for hit in results['result']['hits']:
	    print(f"id: {hit['_id']:<5} | score: {round(hit['_score'], 2):<5} | text: {hit['fields']['chunk_text']:<50}")

def vectors_search(query_text: str, top_k: int = 10):
    #Perform search
    results = search_query(pc.Index("quickstart-py"), query_text=query_text, namespace="namespace", top_k=top_k)
    #print_search_results(results)
    return results.result.hits

def vector_search(query_text: str, top_k: int = 10): 
    """Perform search and return serializable results"""
    try:
        results = search_query(pc.Index("quickstart-py"), query_text=query_text, namespace="namespace", top_k=top_k)
        
        if 'result' in results and 'hits' in results['result']:
            formatted_results = []
            for hit in results['result']['hits']:
                formatted_results.append({
                    'id': hit['_id'],
                    'score': hit['_score'],
                    'text': hit['fields']['chunk_text']
                })
            return formatted_results
        else:
            return []
            
    except Exception as e:
        print(f"Search error: {e}")
        return []
    

# tool dictionary
tool_dict = {
    "name": "vector_search",
    "description": "Performs a semantic search on the vector database of Obama tweets. Call this when you need access to relevant context.",
    "parameters": {
        "type": "object",
        "properties": {
            "query_text": {
                "type": "string",
                "description": "The user query to search against the embedded records."
            },
            "index_name": {
                "type": "string",
                "description": "Name of the Pinecone index to use or create.",
                "default": "quickstart-py"
            },
        },
        "required": ["query_text"]
    }
}


tools = [
    {
        "type": "function",
        "function": tool_dict
    }
]

def handle_tool_call(tool_call):
    arguments = json.loads(tool_call.function.arguments)

    if tool_call.function.name == "vector_search":
        query_text = arguments["query_text"]
        top_k = arguments.get("top_k", 10)

        results = vector_search(
            query_text=query_text,
            top_k=top_k
        )

        return {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(results)
        }
    

#if i want to include multiple tool calls
#tool_responses = []
#for tool_call in tool_calls:
#    tool_responses.append(handle_tool_call(tool_call))

def chat(message, history):
    messages = [{"role": "system", "content": system_message}] + history + [{"role": "user", "content": message}]
    response = client.chat.completions.create(model='gpt-5', messages=messages, tools=tools)

    if response.choices[0].finish_reason == 'tool_calls':
        tool_calls = response.choices[0].message.tool_calls
        for tool_call in tool_calls:
            tool_response = handle_tool_call(tool_call)
            messages.append({"role": "assistant","content": None, "tool_calls": [tool_call]})
            messages.append(tool_response)

        # call the model again with tool response added
        response = client.chat.completions.create(model='gpt-5', messages=messages)

    reply = response.choices[0].message.content
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    return history


def main(message):
    history = []
    history = chat(message, history)
    print(history[-1]["content"])
    
#main("What do you think about Michelle Obama?")


class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Endpoint that calls your existing chat function
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    history = []
    history = chat(req.message, history)  # your existing chat() function
    reply = history[-1]["content"]
    return {"response": reply}

# Only start the server if this file is run directly
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)