"""
Professional RAG Chatbot Application
Clean UI with proper workflow and comparison feature
"""

import streamlit as st
import os
from typing import List, Dict, Any
import tempfile
import requests
from datetime import datetime
from dotenv import load_dotenv

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# Neo4j
from neo4j import GraphDatabase
import json

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling - Clean and minimal
st.markdown("""
<style>
    /* Main background */
    .main {
        background-color: #0f1419;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem 1.2rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    
    .chat-message.user {
        background-color: #1e40af;
        margin-left: 15%;
        border-left: 3px solid #3b82f6;
    }
    
    .chat-message.assistant {
        background-color: #1f2937;
        margin-right: 15%;
        border-left: 3px solid #10b981;
    }
    
    .chat-message .message {
        color: #f3f4f6;
        line-height: 1.6;
        margin-top: 0.5rem;
    }
    
    .chat-message .header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: #9ca3af;
    }
    
    .chat-message .name {
        font-weight: 600;
        color: #e5e7eb;
    }
    
    .source-badge {
        display: inline-block;
        background-color: rgba(16, 185, 129, 0.2);
        color: #10b981;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-top: 0.5rem;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    /* Cards */
    .info-card {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .success-card {
        background-color: #064e3b;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #d1fae5;
    }
    
    .warning-card {
        background-color: #78350f;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        color: #fef3c7;
    }
    
    /* Steps */
    .step-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #374151;
        border-radius: 6px;
            color:white;
    }
    
    .step-item.completed {
        background-color: #065f46;
            color:white;
    }
    
    .step-number {
        background-color: #6b7280;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .step-item.completed .step-number {
        background-color: #10b981;
    }
    
    /* Comparison table */
    .comparison-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .comparison-card {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        padding: 1.5rem;
    }
    
    .comparison-card h4 {
        color: #10b981;
        margin-bottom: 1rem;
        font-size: 1.1rem;
    }
    
    .comparison-card .answer {
        color: #e5e7eb;
        line-height: 1.6;
        font-size: 0.9rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize all session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'documents' not in st.session_state:
        st.session_state.documents = []
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'graph_store' not in st.session_state:
        st.session_state.graph_store = None
    if 'agentic_rag' not in st.session_state:
        st.session_state.agentic_rag = None
    if 'selected_rag_type' not in st.session_state:
        st.session_state.selected_rag_type = None
    if 'indices_built' not in st.session_state:
        st.session_state.indices_built = False
    if 'source_type' not in st.session_state:
        st.session_state.source_type = "PDF"
    if 'config_locked' not in st.session_state:
        st.session_state.config_locked = False

def load_config() -> Dict[str, str]:
    """Load configuration from environment variables"""
    return {
        'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
        'serp_api_key': os.getenv('SERPAPI_KEY', ''),
        'neo4j_uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        'neo4j_user': os.getenv('NEO4J_USER', 'neo4j'),
        'neo4j_password': os.getenv('NEO4J_PASSWORD', ''),
    }

def validate_config(config: Dict[str, str]) -> tuple[bool, List[str]]:
    """Validate required configuration"""
    missing = []
    if not config['openai_api_key']:
        missing.append("OPENAI_API_KEY")
    if not config['serp_api_key']:
        missing.append("SERPAPI_KEY")
    if not config['neo4j_password']:
        missing.append("NEO4J_PASSWORD")
    return len(missing) == 0, missing

def get_llm_response(llm, prompt: str) -> str:
    """Get response from LLM, handling both old and new LangChain APIs"""
    try:
        response = llm.invoke(prompt)
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    except (AttributeError, TypeError):
        try:
            return llm.predict(prompt) if hasattr(llm, 'predict') else str(llm(prompt))
        except:
            return str(response)

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

# RAG Classes
class VectorRAG:
    """Vector Database RAG using FAISS"""
    
    def __init__(self, api_key: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.llm = ChatOpenAI(temperature=0.7, model_name="openai/gpt-4o-mini", openai_api_key=api_key)
        self.vector_store = None
        
    def create_vector_store(self, documents: List[Document]):
        """Create FAISS vector store"""
        try:
            if not documents:
                raise ValueError("No documents provided")
            self.vector_store = FAISS.from_documents(documents=documents, embedding=self.embeddings)
            return True
        except Exception as e:
            st.error(f"Error creating vector store: {str(e)}")
            return False
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the vector store"""
        try:
            if not self.vector_store:
                raise ValueError("Vector store not initialized")
            
            docs = self.vector_store.similarity_search(question, k=3)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            system_message = """You are a helpful AI assistant. Use the provided context to answer questions accurately.

Context:
{context}

Answer the question based on the context. If unsure, say so."""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_message),
                ("human", "{question}")
            ])
            
            formatted = prompt.format_messages(context=context, question=question)
            response = self.llm.invoke(formatted)
            
            return {
                "answer": response.content,
                "sources": f"Vector DB ({len(docs)} docs)",
                "source_count": len(docs)
            }
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "sources": "Error", "source_count": 0}

class KnowledgeGraphRAG:
    """Knowledge Graph RAG using Neo4j"""
    
    def __init__(self, api_key: str, neo4j_uri: str, neo4j_user: str, neo4j_password: str):
        self.llm = ChatOpenAI(temperature=0.7, model_name="openai/gpt-4o-mini", openai_api_key=api_key)
        self.driver = None
        
        try:
            self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.driver.verify_connectivity()
        except Exception as e:
            st.error(f"Neo4j connection error: {str(e)}")
    
    def extract_entities_and_relations(self, text: str) -> Dict[str, Any]:
        """Extract entities and relationships using LLM"""
        try:
            prompt = f"""Extract entities and relationships from the following text.
Return a JSON object with 'entities' (list of {{name, type}}) and 'relationships' (list of {{source, relation, target}}).

Text: {text[:500]}

JSON:"""
            
            response_text = get_llm_response(self.llm, prompt)
            
            try:
                result = json.loads(response_text)
            except:
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {"entities": [], "relationships": []}
            
            return result
        except Exception as e:
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
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, doc in enumerate(documents[:10]):
                status_text.text(f"Processing document {idx + 1}/{min(len(documents), 10)}...")
                
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
                
                progress_bar.progress((idx + 1) / min(len(documents), 10))
            
            status_text.empty()
            progress_bar.empty()
            
            return True, total_entities, total_relations
        except Exception as e:
            st.error(f"Error building knowledge graph: {str(e)}")
            return False, 0, 0
    
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
            
            prompt = f"""Based on the knowledge graph relationships, answer the question.

Knowledge Graph:
{context}

Question: {question}

Answer:"""
            
            answer = get_llm_response(self.llm, prompt)
            
            return {"answer": answer, "sources": "Knowledge Graph", "source_count": len(context_parts)}
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "sources": "Error", "source_count": 0}

class AgenticRAG:
    """Agentic RAG with web search fallback"""
    
    def __init__(self, api_key: str, serp_api_key: str, vector_store=None):
        self.llm = ChatOpenAI(temperature=0.7, model_name="openai/gpt-4o-mini", openai_api_key=api_key)
        self.serp_api_key = serp_api_key
        self.vector_store = vector_store
        
    def search_web(self, query: str) -> str:
        """Search web using SerpAPI"""
        try:
            url = "https://www.searchapi.io/api/v1/search"
            params = {"q": query, "api_key": self.serp_api_key, "engine": "google"}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic_results", [])[:3]:
                results.append(f"• {item.get('title', '')}\n  {item.get('snippet', '')}")
            
            return "\n\n".join(results) if results else "No results found"
        except Exception as e:
            return f"Web search error: {str(e)}"
    
    def search_documents(self, query: str) -> str:
        """Search local documents"""
        try:
            if not self.vector_store:
                return None
            docs = self.vector_store.similarity_search(query, k=3)
            return "\n\n".join([doc.page_content for doc in docs])
        except Exception as e:
            return None
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query using intelligent fallback strategy"""
        try:
            if self.vector_store:
                doc_results = self.search_documents(question)
                if doc_results and "error" not in doc_results.lower() and "not available" not in doc_results.lower() and "does not contain" not in doc_results.lower() and is_relevant(self,question, doc_results):
                    prompt = f"""Using the document information, answer the question.

Documents:
{doc_results}

Question: {question}

Answer:"""
                    answer = get_llm_response(self.llm, prompt)
                    return {"answer": answer, "sources": "Local Documents", "source_count": 3}
            
            web_results = self.search_web(question)
            
            if web_results and "error" not in web_results.lower():
                prompt = f"""Using the web search results, answer the question.

Web Results:
{web_results}

Question: {question}

Answer:"""
                answer = get_llm_response(self.llm, prompt)
                return {"answer": answer, "sources": "Web Search", "source_count": 3}
            
            answer = get_llm_response(self.llm, f"Answer this question: {question}")
            return {"answer": answer, "sources": "AI Knowledge", "source_count": 0}
            
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "sources": "Error", "source_count": 0}

def display_message(role: str, content: str, timestamp: str = None, sources: str = None):
    """Display a chat message"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%I:%M %p")
    
    css_class = "user" if role == "user" else "assistant"
    icon = "👤" if role == "user" else "🤖"
    name = "You" if role == "user" else "Assistant"
    
    # Check if this is a comparison message
    is_comparison = sources == "Comparison Mode" if sources else False
    
    message_html = f"""
    <div class="chat-message {css_class}">
        <div class="header">
            <span>{icon}</span>
            <span class="name">{name}</span>
            <span>• {timestamp}</span>
        </div>
        <div class="message">{content}</div>
    """
    
    if sources and role == "assistant":
        if is_comparison:
            message_html += f'<div class="source-badge">📊 {sources}</div>'
        else:
            message_html += f'<div class="source-badge">{sources}</div>'
    
    message_html += "</div>"
    st.markdown(message_html, unsafe_allow_html=True)

def build_rag_index(config: Dict[str, str], rag_type: str) -> bool:
    """Build specific RAG index based on selected type"""
    try:
        if rag_type == "Vector DB RAG":
            with st.status("Building Vector Database...", expanded=True) as status:
                st.write("Creating embeddings...")
                vector_rag = VectorRAG(config['openai_api_key'])
                if vector_rag.create_vector_store(st.session_state.documents):
                    st.session_state.vector_store = vector_rag
                    st.write("✅ Vector database created")
                    status.update(label="✅ Vector DB ready!", state="complete", expanded=False)
                    return True
                return False
        
        elif rag_type == "Knowledge Graph RAG":
            with st.status("Building Knowledge Graph...", expanded=True) as status:
                st.write("Extracting entities and relationships...")
                kg_rag = KnowledgeGraphRAG(
                    config['openai_api_key'],
                    config['neo4j_uri'],
                    config['neo4j_user'],
                    config['neo4j_password']
                )
                success, entities, relations = kg_rag.build_knowledge_graph(st.session_state.documents)
                if success:
                    st.session_state.graph_store = kg_rag
                    st.write(f"✅ Knowledge graph created ({entities} entities, {relations} relationships)")
                    status.update(label="✅ Knowledge Graph ready!", state="complete", expanded=False)
                    return True
                return False
        
        elif rag_type == "Agentic RAG":
            with st.status("Initializing Agentic RAG...", expanded=True) as status:
                st.write("Setting up vector store for documents...")
                vector_rag = VectorRAG(config['openai_api_key'])
                if vector_rag.create_vector_store(st.session_state.documents):
                    st.session_state.vector_store = vector_rag
                    vector_store = vector_rag.vector_store
                else:
                    vector_store = None
                
                st.write("Configuring web search...")
                st.session_state.agentic_rag = AgenticRAG(
                    config['openai_api_key'],
                    config['serp_api_key'],
                    vector_store
                )
                st.write("✅ Agentic RAG initialized")
                status.update(label="✅ Agentic RAG ready!", state="complete", expanded=False)
                return True
        
        elif rag_type == "Compare All":
            with st.status("Building all RAG systems...", expanded=True) as status:
                # Vector store
                st.write("1/3 Building Vector Database...")
                vector_rag = VectorRAG(config['openai_api_key'])
                if vector_rag.create_vector_store(st.session_state.documents):
                    st.session_state.vector_store = vector_rag
                    st.write("✅ Vector DB ready")
                
                # Knowledge graph
                st.write("2/3 Building Knowledge Graph...")
                kg_rag = KnowledgeGraphRAG(
                    config['openai_api_key'],
                    config['neo4j_uri'],
                    config['neo4j_user'],
                    config['neo4j_password']
                )
                success, entities, relations = kg_rag.build_knowledge_graph(st.session_state.documents)
                if success:
                    st.session_state.graph_store = kg_rag
                    st.write(f"✅ Knowledge Graph ready")
                
                # Agentic RAG
                st.write("3/3 Initializing Agentic RAG...")
                vector_store = st.session_state.vector_store.vector_store if st.session_state.vector_store else None
                st.session_state.agentic_rag = AgenticRAG(
                    config['openai_api_key'],
                    config['serp_api_key'],
                    vector_store
                )
                st.write("✅ Agentic RAG ready")
                
                status.update(label="✅ All RAG systems ready!", state="complete", expanded=False)
                return True
        
        return False
    except Exception as e:
        st.error(f"Error building index: {str(e)}")
        return False

def compare_all_rag(question: str) -> Dict[str, Any]:
    """Compare all three RAG systems"""
    results = {}
    
    with st.spinner("Querying all RAG systems..."):
        # Vector RAG
        if st.session_state.vector_store:
            results["vector"] = st.session_state.vector_store.query(question)
        else:
            results["vector"] = {"answer": "Not available", "sources": "N/A"}
        
        # Knowledge Graph RAG
        if st.session_state.graph_store:
            results["kg"] = st.session_state.graph_store.query(question)
        else:
            results["kg"] = {"answer": "Not available", "sources": "N/A"}
        
        # Agentic RAG
        if st.session_state.agentic_rag:
            results["agentic"] = st.session_state.agentic_rag.query(question)
        else:
            results["agentic"] = {"answer": "Not available", "sources": "N/A"}
    
    return results

def show_setup_wizard(config: Dict[str, str]):
    """Display setup wizard"""
    st.markdown("### 🚀 Setup Your RAG Chatbot")
    st.markdown("Follow these steps to get started")
    
    # Step 1: Choose RAG Type
    st.markdown(f"""
    <div class="step-item {'completed' if st.session_state.selected_rag_type else ''}">
        <div class="step-number">1</div>
        <div>
            <strong>Choose RAG Method</strong><br/>
            <small>Select how you want to retrieve information</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.selected_rag_type:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔢 Vector DB", use_container_width=True):
                st.session_state.selected_rag_type = "Vector DB RAG"
                st.rerun()
        
        with col2:
            if st.button("🕸️ Knowledge Graph", use_container_width=True):
                st.session_state.selected_rag_type = "Knowledge Graph RAG"
                st.rerun()
        
        with col3:
            if st.button("🤖 Agentic", use_container_width=True):
                st.session_state.selected_rag_type = "Agentic RAG"
                st.rerun()
        
        with col4:
            if st.button("📊 Compare All", use_container_width=True):
                st.session_state.selected_rag_type = "Compare All"
                st.rerun()
        
        st.info("""
        **Vector DB**: Fast semantic search  
        **Knowledge Graph**: Entity relationships  
        **Agentic**: Smart search with web fallback  
        **Compare All**: See all three methods side-by-side
        """)
        return
    
    st.success(f"✅ Selected: **{st.session_state.selected_rag_type}**")
    
    # Step 2: Upload Documents
    st.markdown(f"""
    <div class="step-item {'completed' if st.session_state.documents else ''}">
        <div class="step-number">2</div>
        <div>
            <strong>Upload Data Source</strong><br/>
            <small>Provide documents for the chatbot to learn from</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.documents:
        # Source type toggle
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 PDF File", use_container_width=True, 
                        type="primary" if st.session_state.source_type == "PDF" else "secondary"):
                st.session_state.source_type = "PDF"
                st.rerun()
        with col2:
            if st.button("🌐 Web URL", use_container_width=True,
                        type="primary" if st.session_state.source_type == "URL" else "secondary"):
                st.session_state.source_type = "URL"
                st.rerun()
        
        st.markdown("---")
        
        if st.session_state.source_type == "PDF":
            uploaded_file = st.file_uploader(
                "Upload PDF file (max 500KB)",
                type=['pdf'],
                key="pdf_uploader"
            )
            
            if uploaded_file:
                if st.button("📤 Process PDF", use_container_width=True, type="primary"):
                    with st.spinner("Processing PDF..."):
                        docs = load_pdf(uploaded_file)
                        if docs:
                            chunks = chunk_documents(docs)
                            st.session_state.documents = chunks
                            st.success(f"✅ Processed {len(chunks)} chunks")
                            st.rerun()
        else:
            url_input = st.text_input(
                "Enter webpage URL",
                placeholder="https://example.com/article"
            )
            
            if url_input:
                if st.button("🔗 Load URL", use_container_width=True, type="primary"):
                    with st.spinner("Loading URL..."):
                        docs = load_url(url_input)
                        if docs:
                            chunks = chunk_documents(docs)
                            st.session_state.documents = chunks
                            st.success(f"✅ Processed {len(chunks)} chunks")
                            st.rerun()
        return
    
    st.success(f"✅ Loaded: **{len(st.session_state.documents)} document chunks**")
    
    # Step 3: Build Knowledge Base
    st.markdown(f"""
    <div class="step-item {'completed' if st.session_state.indices_built else ''}">
        <div class="step-number">3</div>
        <div>
            <strong>Build Knowledge Base</strong><br/>
            <small>Create searchable index from your documents</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.indices_built:
        if st.button("🔨 Build Knowledge Base", type="primary", use_container_width=True):
            success = build_rag_index(config, st.session_state.selected_rag_type)
            if success:
                st.session_state.indices_built = True
                st.session_state.config_locked = True
                st.success("✅ Knowledge base built successfully!")
                st.balloons()
                st.rerun()
    else:
        st.success("✅ **Setup Complete!** You can now start chatting.")

def show_chat_interface(config: Dict[str, str]):
    """Display chat interface"""
    
    # Display chat history
    for message in st.session_state.messages:
        display_message(
            message["role"],
            message["content"],
            message.get("timestamp"),
            message.get("sources")
        )
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        timestamp = datetime.now().strftime("%I:%M %p")
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        
        display_message("user", prompt, timestamp)
        
        # Get response
        with st.spinner("Thinking..."):
            try:
                if st.session_state.selected_rag_type == "Compare All":
                    # Show comparison
                    results = compare_all_rag(prompt)
                    
                    # Create comparison summary for chat history
                    comparison_summary = f"""**Comparison Results:**

**🔢 Vector DB RAG**
{results["vector"]["answer"]}
_Source: {results['vector'].get('sources', 'N/A')}_

**🕸️ Knowledge Graph RAG**
{results["kg"]["answer"]}
_Source: {results['kg'].get('sources', 'N/A')}_

**🤖 Agentic RAG**
{results["agentic"]["answer"]}
_Source: {results['agentic'].get('sources', 'N/A')}_"""
                    
                    # Add to message history
                    assistant_timestamp = datetime.now().strftime("%I:%M %p")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": comparison_summary,
                        "timestamp": assistant_timestamp,
                        "sources": "Comparison Mode"
                    })
                    
                    # Display comparison in columns
                    st.markdown("### 📊 Comparison Results")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("#### 🔢 Vector DB RAG")
                        st.write(results["vector"]["answer"])
                        st.caption(f"📚 {results['vector'].get('sources', 'N/A')}")
                    
                    with col2:
                        st.markdown("#### 🕸️ Knowledge Graph RAG")
                        st.write(results["kg"]["answer"])
                        st.caption(f"📚 {results['kg'].get('sources', 'N/A')}")
                    
                    with col3:
                        st.markdown("#### 🤖 Agentic RAG")
                        st.write(results["agentic"]["answer"])
                        st.caption(f"📚 {results['agentic'].get('sources', 'N/A')}")
                    
                    return
                
                # Single RAG query
                if st.session_state.selected_rag_type == "Vector DB RAG":
                    result = st.session_state.vector_store.query(prompt)
                elif st.session_state.selected_rag_type == "Knowledge Graph RAG":
                    result = st.session_state.graph_store.query(prompt)
                else:  # Agentic RAG
                    result = st.session_state.agentic_rag.query(prompt)
                
                # Add assistant message
                assistant_timestamp = datetime.now().strftime("%I:%M %p")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "timestamp": assistant_timestamp,
                    "sources": result.get("sources", "Unknown")
                })
                
                display_message(
                    "assistant",
                    result["answer"],
                    assistant_timestamp,
                    result.get("sources")
                )
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "timestamp": datetime.now().strftime("%I:%M %p"),
                    "sources": "Error"
                })
                display_message("assistant", error_msg)

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

def main():
    initialize_session_state()
    
    config = load_config()
    is_valid, missing = validate_config(config)
    
    st.title("💬 RAG Chatbot")
    
    if not is_valid:
        st.error(f"❌ Missing environment variables: {', '.join(missing)}")
        st.info("Please create a `.env` file with required API keys. See `.env.example` for reference.")
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        st.success("✅ Loaded from .env")
        
        if st.session_state.selected_rag_type:
            st.markdown("---")
            st.markdown("### 📋 Current Setup")
            st.info(f"**Method**: {st.session_state.selected_rag_type}")
            
            if st.session_state.documents:
                st.metric("Documents", len(st.session_state.documents))
            
            if st.session_state.messages:
                st.metric("Messages", len(st.session_state.messages))
        
        st.markdown("---")
        
        if st.session_state.config_locked:
            if st.button("🔄 Reset Configuration", use_container_width=True, type="secondary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
            
            if st.session_state.messages:
                if st.button("🗑️ Clear Chat", use_container_width=True):
                    st.session_state.messages = []
                    st.rerun()
    
    # Main content
    if not st.session_state.indices_built:
        show_setup_wizard(config)
    else:
        st.markdown("### 💬 Chat with Your Documents")
        if st.session_state.selected_rag_type == "Compare All":
            st.info("💡 In comparison mode, each question will show results from all three RAG methods side-by-side.")
        show_chat_interface(config)

if __name__ == "__main__":
    main()