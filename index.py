from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader,SimpleKeywordTableIndex
from llama_index.core import Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
# from IPython.display import Markdown, display
from llama_index.llms.ollama import Ollama
from db import DB
from llm import CustomLlama2
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core import PromptTemplate
from llama_index.llms.llama_cpp.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)
from datetime import datetime 

qa_prompt_tmpl = PromptTemplate(
    "Here is a list of news articles from the New York Times\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query. Today is {date}.\n"
    "Query: {query_str}\n"
    "Answer: "
)
qa_prompt_tmpl = qa_prompt_tmpl.partial_format(date=datetime.now().strftime("%Y-%m-%d"))

class Index:
    def __init__(self, documents=[], embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"), load_from_disk=True):
        
        Settings.embed_model = embed_model
        Settings.llm = Ollama(model="llama3:latest", request_timeout=60.0, max_tokens=100, temperature=0.1, context_window=4096)
        self.chroma_db = DB()
        self.vector_store = ChromaVectorStore(chroma_collection=self.chroma_db.collection, persist_dir="./chroma_db")
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        self.documents = documents
        if len(self.documents) > 0:
            pipeline = IngestionPipeline(
                transformations=[
                    embed_model,
                ],
                docstore=SimpleDocumentStore(),
                vector_store=self.vector_store,
            )
            pipeline.run(documents=self.documents, show_progress=True)
        self.index = VectorStoreIndex.from_vector_store(self.vector_store)
        # self.keyword_index = SimpleKeywordTableIndex.from_documents(documents, storage_context=self.storage_context, show_progress=True)
        self.query_engine = self.index.as_query_engine(streaming=True, similarity_top_k=5)
        self.query_engine.update_prompts({"response_synthesizer:text_qa_template": qa_prompt_tmpl})
        
        self.chat_engine = self.index.as_chat_engine()
    
    def chat(self, query_text):
        stream = self.chat_engine.stream_chat(query_text)
        response = ""
        for token in stream.response_gen:
            response += token
            print(token, end="")
        return response #self.query_engine.query(query_text)
    
    def query(self, query_text):
        response = self.query_engine.query(query_text)
        return response
    
if __name__ == "__main__":
    index = Index()
    query_engine = index.index.as_query_engine(response_mode="compact")
    prompts_dict = query_engine.get_prompts()
    print(list(prompts_dict.keys()))