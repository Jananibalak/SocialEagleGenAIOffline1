"""
Streamlit RAG Application - Simplified Version
Compatible with latest LangChain versions
"""

import streamlit as st
import os
import dotenv
from typing import List, Dict, Any
import tempfile
import requests

# LangChain imports - simplified
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
load_dotenv()


# Neo4j
from neo4j import GraphDatabase
import json

# Configure page
st.set_page_config(
    page_title="Advanced RAG System",
    page_icon="🤖",
    layout="wide"
)



def initialize_session_state():
    """Initialize session state variables"""
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'graph_store' not in st.session_state:
        st.session_state.graph_store = None

# Document Processing Functions
def load_pdf(file) -> List[Document]:
    """Load and process PDF file"""
    try:
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > 500 * 1024:
            st.error(f"File size ({file_size / 1024:.2f}KB) exceeds 500KB limit")
            return []
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name
        
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        os.unlink(tmp_path)
        
        return documents
    except Exception as e:
        st.error(f"Error loading PDF: {str(e)}")
        return []

def load_url(url: str) -> List[Document]:
    """Load content from URL"""
    try:
        loader = WebBaseLoader(url)
        documents = loader.load()
        return documents
    except Exception as e:
        st.error(f"Error loading URL: {str(e)}")
        return []

def chunk_documents(documents: List[Document], chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """Split documents into chunks"""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        return chunks
    except Exception as e:
        st.error(f"Error chunking documents: {str(e)}")
        return []

# Vector RAG Class
class VectorRAG:
    """Vector Database RAG using FAISS"""
    
    def __init__(self, api_key: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.llm = ChatOpenAI(temperature=0, model_name="openai/gpt-4o-mini", openai_api_key=api_key)
        self.vector_store = None
        
    def create_vector_store(self, documents: List[Document]):
        """Create FAISS vector store"""
        try:
            if not documents:
                raise ValueError("No documents provided")
            self.vector_store = FAISS.from_documents(documents=documents, embedding=self.embeddings)
            st.success(f"✅ Vector store created with {len(documents)} chunks")
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            raise
    
    def query(self, question: str, k: int = 3) -> Dict[str, Any]:
        """Query the vector store"""
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            prompt_template = """Use the following pieces of context to answer the question at the end. 
            If you don't know the answer, just say that you don't know, don't try to make up an answer.

            Context: {context}
            Question: {question}
            
            Answer:"""
            
            PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
            retriever = self.vector_store.as_retriever(search_kwargs={"k": k})
            chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough()
        }
        | PROMPT
        | self.llm
        | StrOutputParser()
        )
            
            answer = chain.invoke(question)

            docs = retriever.invoke(question)

            return {
            "answer": answer,
            "source_documents": docs
            }
        except Exception as e:
            st.error(f"Error querying vector store: {str(e)}")
            return {"answer": f"Error: {str(e)}", "source_documents": []}

# Knowledge Graph RAG Class
class KnowledgeGraphRAG:
    """Knowledge Graph RAG using Neo4j"""
    
    def __init__(self, api_key: str, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.llm = ChatOpenAI(temperature=0, model_name="openai/gpt-4o-mini", openai_api_key=api_key)
        
        try:
            self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.driver.verify_connectivity()
        except Exception as e:
            st.error(f"Neo4j connection error: {str(e)}")
            self.driver = None
    
    def extract_entities_and_relations(self, text: str) -> Dict[str, Any]:
        """Extract entities and relationships using LLM"""
        try:
            prompt = f"""Extract entities and relationships from the following text.
            Return a JSON object with 'entities' (list of {{name, type}}) and 
            'relationships' (list of {{source, relation, target}}).
            
            Text: {text}
            
            JSON:"""
            
            response = self.llm.invoke(prompt).content
            
            try:
                result = json.loads(response)
            except:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"entities": [], "relationships": []}
            
            return result
        except Exception as e:
            st.error(f"Error extracting entities: {str(e)}")
            return {"entities": [], "relationships": []}
    
    def build_knowledge_graph(self, documents: List[Document]):
        """Build knowledge graph from documents"""
        try:
            if not self.driver:
                raise ValueError("Neo4j not connected")
            
            with self.driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            
            total_entities = 0
            total_relations = 0
            
            for doc in documents:
                extracted = self.extract_entities_and_relations(doc.page_content)
                
                with self.driver.session() as session:
                    for entity in extracted.get("entities", []):
                        session.run(
                            "MERGE (e:Entity {name: $name, type: $type})",
                            name=entity.get("name", ""),
                            type=entity.get("type", "Unknown")
                        )
                        total_entities += 1
                    
                    for rel in extracted.get("relationships", []):
                        session.run(
                            """MATCH (a:Entity {name: $source})
                               MATCH (b:Entity {name: $target})
                               MERGE (a)-[r:RELATES {type: $relation}]->(b)""",
                            source=rel.get("source", ""),
                            target=rel.get("target", ""),
                            relation=rel.get("relation", "RELATED_TO")
                        )
                        total_relations += 1
            
            st.success(f"✅ Knowledge graph created with {total_entities} entities and {total_relations} relationships")
        except Exception as e:
            st.error(f"Error building knowledge graph: {str(e)}")
            raise
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the knowledge graph"""
        try:
            if not self.driver:
                raise ValueError("Neo4j not connected")
            
            entities_data = self.extract_entities_and_relations(question)
            entities = [e.get("name", "") for e in entities_data.get("entities", [])]
            
            context_parts = []
            with self.driver.session() as session:
                for entity in entities:
                    result = session.run(
                        """MATCH (e:Entity {name: $entity})-[r]-(connected)
                           RETURN e.name as entity, type(r) as relation, 
                                  connected.name as connected_entity
                           LIMIT 5""",
                        entity=entity
                    )
                    
                    for record in result:
                        context_parts.append(
                            f"{record['entity']} {record['relation']} {record['connected_entity']}"
                        )
            
            if not context_parts:
                with self.driver.session() as session:
                    result = session.run(
                        """MATCH (e:Entity)-[r]-(connected)
                           RETURN e.name as entity, type(r) as relation, 
                                  connected.name as connected_entity
                           LIMIT 10"""
                    )
                    for record in result:
                        context_parts.append(
                            f"{record['entity']} {record['relation']} {record['connected_entity']}"
                        )
            
            context = "\n".join(context_parts) if context_parts else "No relevant graph data found"
            
            prompt = f"""Based on the following knowledge graph information, answer the question.
            
            Knowledge Graph Context:
            {context}
            
            Question: {question}
            
            Answer:"""
            
            answer = self.llm.invoke(prompt).content
            
            return {"answer": answer, "context": context}
        except Exception as e:
            st.error(f"Error querying knowledge graph: {str(e)}")
            return {"answer": f"Error: {str(e)}", "context": ""}
    
    def close(self):
        if self.driver:
            self.driver.close()

# Agentic RAG Class (Simplified)
class AgenticRAG:
    """Agentic RAG with web search fallback - Simplified version"""
    
    def __init__(self, api_key: str, serp_api_key: str, vector_store=None):
        self.llm = ChatOpenAI(temperature=0, model_name="openai/gpt-4o-mini", openai_api_key=api_key)
        self.serp_api_key = serp_api_key
        self.vector_store = vector_store
        
    def search_web(self, query: str) -> str:
        """Search web using SerpAPI"""
        try:
            url = "https://serpapi.com/search"
            params = {"q": query, "api_key": self.serp_api_key, "engine": "google"}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic_results", [])[:3]:
                results.append(f"Title: {item.get('title', '')}\nSnippet: {item.get('snippet', '')}")
            
            return "\n\n".join(results) if results else "No results found"
        except Exception as e:
            return f"Web search error: {str(e)}"
    
    def search_documents(self, query: str) -> str:
        """Search local documents"""
        try:
            if not self.vector_store:
                return "No document store available"
            docs = self.vector_store.similarity_search(query, k=3)
            return "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            return f"Document search error: {str(e)}"
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query using intelligent fallback strategy"""
        try:
            # Step 1: Try document search first
            if self.vector_store:
                doc_results = self.search_documents(question)
                if doc_results and "error" not in doc_results.lower() and "not available" not in doc_results.lower() and "does not contain" not in doc_results.lower() and is_relevant(self,question, doc_results):
                    prompt = f"""Based on the following document information, answer the question.
                    
Document Information:
{doc_results}

Question: {question}

Answer:"""
                    answer = self.llm.invoke(prompt).content
                    return {"answer": answer, "sources": "Local documents"}
            
             # Step 2: Fallback to web search
            st.info("🌐 Searching the web for current information...")
            web_results = self.search_web(question)
            
            if web_results and "error" not in web_results.lower():
                prompt = f"""Based on the following web search results, answer the question.
                
Web Search Results:
{web_results}

Question: {question}

Answer:"""
                answer = self.llm.invoke(prompt).content
                return {"answer": answer, "sources": "Web search"}
            
            # Step 3: Final fallback to LLM knowledge
            st.warning("⚠️ Using LLM knowledge only (no external sources)")
            answer = self.llm.invoke(f"Answer this question: {question}").content
            return {"answer": answer, "sources": "LLM knowledge"}
            
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "sources": "Error"}

# Comparison Function
def compare_rag_systems(question: str, vector_rag, kg_rag, agentic_rag) -> Dict[str, Any]:
    """Compare all three RAG systems"""
    results = {}
    
    with st.spinner("Querying Vector DB RAG..."):
        try:
            results["vector"] = vector_rag.query(question)
        except Exception as e:
            results["vector"] = {"answer": f"Error: {str(e)}", "source_documents": []}
    
    with st.spinner("Querying Knowledge Graph RAG..."):
        try:
            results["kg"] = kg_rag.query(question)
        except Exception as e:
            results["kg"] = {"answer": f"Error: {str(e)}", "context": ""}
    
    with st.spinner("Querying Agentic RAG..."):
        try:
            results["agentic"] = agentic_rag.query(question)
        except Exception as e:
            results["agentic"] = {"answer": f"Error: {str(e)}", "sources": ""}
    
    return results


def is_relevant(self, question: str, context: str) -> bool:
    prompt = f"""
Question: {question}

Context:
{context}

Does the context contain information that can directly answer the question?
Reply with only YES or NO.
"""
    response = self.llm.invoke(prompt).content.strip().upper()
    print(response == "YES")
    return response == "YES"


# Main Application
def main():
    initialize_session_state()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    serp_api_key = os.getenv('SERPAPI_KEY')
    neo4j_uri = os.getenv('NEO4J_URI')
    neo4j_user = os.getenv('NEO4J_USER')
    neo4j_password = os.getenv('NEO4J_PASSWORD')
    st.title("🤖 Advanced RAG System")
    st.markdown("""
    Upload documents or URLs and query them using different RAG approaches:
    - **Vector DB RAG**: FAISS-based semantic search
    - **Knowledge Graph RAG**: Neo4j-based entity relationships
    - **Agentic RAG**: Intelligent search with web fallback
    """)
    
    # Sidebar
    with st.sidebar:

        

        st.header("📁 Data Sources")
        
        upload_type = st.radio("Source Type", ["Upload PDF", "Load from URL"])
        
        if upload_type == "Upload PDF":
            uploaded_file = st.file_uploader("Upload PDF (max 500KB)", type=['pdf'])
            
            if uploaded_file and st.button("Process PDF"):
                if not openai_api_key:
                    st.error("Please enter OpenAI API key")
                else:
                    with st.spinner("Processing PDF..."):
                        docs = load_pdf(uploaded_file)
                        if docs:
                            chunks = chunk_documents(docs)
                            st.session_state.documents = chunks
                            st.success(f"✅ Processed {len(chunks)} chunks")
        else:
            url_input = st.text_input("Enter URL")
            if url_input and st.button("Load URL"):
                if not openai_api_key:
                    st.error("Please enter OpenAI API key")
                else:
                    with st.spinner("Loading URL..."):
                        docs = load_url(url_input)
                        if docs:
                            chunks = chunk_documents(docs)
                            st.session_state.documents = chunks
                            st.success(f"✅ Processed {len(chunks)} chunks")
        
        if st.session_state.documents and st.button("🔨 Build RAG Indices"):
            if not all([openai_api_key, serp_api_key, neo4j_password]):
                st.error("Please enter all required API keys")
            else:
                with st.spinner("Building indices..."):
                    try:
                        vector_rag = VectorRAG(openai_api_key)
                        vector_rag.create_vector_store(st.session_state.documents)
                        st.session_state.vector_store = vector_rag
                    except Exception as e:
                        st.error(f"Vector store error: {str(e)}")
                    
                    try:
                        kg_rag = KnowledgeGraphRAG(openai_api_key, neo4j_uri, neo4j_user, neo4j_password)
                        kg_rag.build_knowledge_graph(st.session_state.documents)
                        st.session_state.graph_store = kg_rag
                    except Exception as e:
                        st.error(f"Knowledge graph error: {str(e)}")
    
    # Main content
    if not st.session_state.documents:
        st.info("👈 Please upload documents or load a URL from the sidebar to get started")
        return
    
    st.header("🔍 Query Your Data")
    
    rag_type = st.selectbox(
        "Select RAG Type",
        ["Vector DB RAG", "Knowledge Graph RAG", "Agentic RAG", "Compare All"]
    )
    
    question = st.text_input("Enter your question:", placeholder="What is this document about?")
    
    if st.button("Get Answer", type="primary"):
        if not question:
            st.warning("Please enter a question")
            return
        
        if not all([openai_api_key, serp_api_key]):
            st.error("Please enter all required API keys in the sidebar")
            return
        
        if rag_type == "Vector DB RAG":
            if not st.session_state.vector_store:
                st.error("Please build indices first")
                return
            
            with st.spinner("Searching..."):
                result = st.session_state.vector_store.query(question)
                st.subheader("📝 Answer")
                st.write(result["answer"])
                
                with st.expander("📚 Source Documents"):
                    for i, doc in enumerate(result["source_documents"]):
                        st.markdown(f"**Source {i+1}:**")
                        st.text(doc.page_content[:500] + "...")
        
        elif rag_type == "Knowledge Graph RAG":
            if not st.session_state.graph_store:
                st.error("Please build indices first")
                return
            
            with st.spinner("Querying graph..."):
                result = st.session_state.graph_store.query(question)
                st.subheader("📝 Answer")
                st.write(result["answer"])
                
                with st.expander("🕸️ Graph Context"):
                    st.code(result["context"])
        
        elif rag_type == "Agentic RAG":
            with st.spinner("Agent working..."):
                vector_store = st.session_state.vector_store.vector_store if st.session_state.vector_store else None
                agentic_rag = AgenticRAG(openai_api_key, serp_api_key, vector_store)
                result = agentic_rag.query(question)
                
                st.subheader("📝 Answer")
                st.write(result["answer"])
                st.info(f"**Sources used:** {result['sources']}")
        
        else:  # Compare All
            if not st.session_state.vector_store or not st.session_state.graph_store:
                st.error("Please build indices first")
                return
            
            vector_store = st.session_state.vector_store.vector_store if st.session_state.vector_store else None
            agentic_rag = AgenticRAG(openai_api_key, serp_api_key, vector_store)
            
            results = compare_rag_systems(
                question,
                st.session_state.vector_store,
                st.session_state.graph_store,
                agentic_rag
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("🔢 Vector DB RAG")
                st.write(results["vector"]["answer"])
                st.caption(f"Sources: {len(results['vector'].get('source_documents', []))} documents")
            
            with col2:
                st.subheader("🕸️ Knowledge Graph RAG")
                st.write(results["kg"]["answer"])
                st.caption("Sources: Graph relationships")
            
            with col3:
                st.subheader("🤖 Agentic RAG")
                st.write(results["agentic"]["answer"])
                st.caption(f"Sources: {results['agentic'].get('sources', 'N/A')}")

if __name__ == "__main__":
    main()