
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS

def get_qa_chain(vector_db: FAISS) -> RetrievalQA:
    llm = Ollama(model="tinyllama")
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        verbose=False,
    )
    return qa_chain
