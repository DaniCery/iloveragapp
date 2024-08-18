from langchain_community.llms import Ollama

# Create an instance of the model
cached_llm = Ollama(model="llama3.1")

# Test the model to ensure it’s working
response = cached_llm.invoke("Hi", endpoint="/v1/chat/completions")
print(response)