from langchain_community.llms import Ollama

llm = Ollama(model="mistral")

response = llm.invoke("Give 3 steps to pick an object")

print(response)