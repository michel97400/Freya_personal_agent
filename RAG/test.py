# Basic example for LlamaIndex

from llama_index import SimpleDirectoryReader, GPTVectorStoreIndex, ServiceContext

# Load documents from a directory (adjust the path as needed)
documents = SimpleDirectoryReader("data").load_data()

# Optional: customize the service context (e.g., LLM, embed model)
service_context = ServiceContext.from_defaults()

# Create the index
index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)

# Query the index
query_engine = index.as_query_engine()
response = query_engine.query("What is the main topic of the documents?")
print(response)
