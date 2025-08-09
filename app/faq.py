import pandas as pd
from pathlib import Path
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS 
from langchain.docstore.document import Document
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

project_root = Path(__file__).resolve().parent.parent
faqs_path = project_root / "resources" / "faq_data.csv"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
collection_name = "faq_collection"
vector_store_path = project_root / "resources" / collection_name

ef = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code": True}
        )

groq_client = Groq()

def create_faq_collection(path):
    """Create a ChromaDB collection for FAQs."""
    if vector_store_path.exists():
        try:
            print(f"📚 Loading existing vector store")
            vector_store = FAISS.load_local(
                str(vector_store_path), 
                embeddings=ef, 
                allow_dangerous_deserialization=True
            )
            print("✅ Successfully loaded existing vector store")

        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            print("🔄 Creating new vector store...")        
    else:
        df = pd.read_csv(path)

        # Create Document objects (not just strings)
        documents = []
        for _, row in df.iterrows():
            doc = Document(
                page_content=row['question'],
                metadata={'answer': row['answer']}
            )
            documents.append(doc)
        
        print("Creating new vector store...")
        vector_store = FAISS.from_documents(
            documents=documents,
            embedding=ef
        ) 
        print("Successfully created vector store")
        vector_store.save_local(str(vector_store_path))
        print("Successfully saved vector store")

def get_relevant_qa(query):
    """Get relevant Q&A pairs from the FAQ collection."""
    vector_store = FAISS.load_local(
        str(vector_store_path), 
        embeddings=ef, 
        allow_dangerous_deserialization=True
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    answers = [doc.metadata['answer'] for doc in retriever.invoke(query)]
    return "\n\n".join(answers)

def generate_answer(context,query):
    """Generate an answer based on the context retrieved from the FAQ collection."""
    prompt = f'''Given the following context and question, generate answer based on this context only.
    If the answer is not found in the context, kindly state "I don't know". Don't try to make up an answer.
    
    CONTEXT: {context}
    
    QUESTION: {query}
    '''
    completion = groq_client.chat.completions.create(
        model=os.environ['GROQ_MODEL'],
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )
    return completion.choices[0].message.content

def faq_chain(query):
    """Chain to handle FAQ queries."""
    create_faq_collection(faqs_path)
    context = get_relevant_qa(query)
    response = generate_answer(context, query)
    return response

if __name__ == "__main__":
    response = faq_chain("Do you except credit card") 
    print(response)
