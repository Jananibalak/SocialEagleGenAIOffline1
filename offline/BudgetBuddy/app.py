"""
BudgetBuddy RAG API - Flask REST API for Bill Analysis
Compatible with LangChain 1.2.10+ and latest package versions
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pathlib import Path
import uuid
from typing import Dict, List, Any

# LangChain imports - Updated for your installed versions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch

# Local imports
from bill_processor import BillProcessor
from analysis_engine import AnalysisEngine

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global storage for sessions (in production, use Redis or database)
sessions = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def initialize_openrouter_client(api_key: str):
    """Initialize OpenRouter client with GPT-4 mini"""
    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.7,
        max_tokens=2000
    )


def create_vectorstore(documents: List[str], api_key: str):
    """Create FAISS vectorstore from documents"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    
    # Create Document objects
    docs = [Document(page_content=doc) for doc in documents]
    chunks = text_splitter.split_documents(docs)
    
    # Use OpenAI embeddings via OpenRouter
    embeddings = OpenAIEmbeddings(
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1"
    )
    
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore


def format_chat_history(chat_history: List[Dict]) -> str:
    """Format chat history into a string for the prompt"""
    if not chat_history:
        return ""
    
    formatted = []
    for chat in chat_history:
        formatted.append(f"Human: {chat['user']}")
        formatted.append(f"Assistant: {chat['assistant']}")
    return "\n".join(formatted)


def create_conversation_chain(vectorstore, llm):
    """
    Create conversational RAG chain using LCEL (LangChain Expression Language)
    This approach works with all LangChain versions
    """
    
    # Create retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # Define the prompt template
    template = """You are BudgetBuddy, a friendly and supportive financial advisor who analyzes bills and expenses. 
You combine the warmth of a caring friend with the expertise of a financial advisor.

Your personality:
- Encouraging and non-judgmental
- Use emojis occasionally to be friendly 😊 💰
- Give practical, actionable advice
- Celebrate wins and gently point out areas for improvement
- Be conversational and relatable

Context from the user's bills:
{context}

Chat History:
{chat_history}

Current Question: {question}

Provide a helpful, friendly response with specific insights from their bills. If you don't have enough information, just say so in a friendly way."""

    prompt = ChatPromptTemplate.from_template(template)
    
    # Create the chain using LCEL
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    
    # Build the chain
    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
            "chat_history": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain, retriever


# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
def home():
    """API home endpoint with documentation"""
    return jsonify({
        'name': 'BudgetBuddy RAG API',
        'version': '1.0.0',
        'description': 'AI-powered bill analysis and financial insights API',
        'endpoints': {
            'POST /api/session/create': 'Create a new session',
            'POST /api/upload': 'Upload and process bills',
            'POST /api/search': 'Search bills with semantic query',
            'POST /api/chat': 'Chat with AI about your bills',
            'GET /api/analysis/<session_id>': 'Get financial analysis',
            'GET /api/bills/<session_id>': 'Get all processed bills',
            'GET /api/session/<session_id>': 'Get session info',
            'DELETE /api/session/<session_id>': 'Delete session'
        },
        'status': 'running'
    }), 200


@app.route('/api/session/create', methods=['POST'])
def create_session():
    """
    Create a new session for bill analysis
    
    Request body:
    {
        "api_key": "your_openrouter_api_key"
    }
    
    Response:
    {
        "session_id": "uuid",
        "created_at": "timestamp",
        "message": "Session created successfully"
    }
    """
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key is required'}), 400
        
        # Create new session
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'api_key': api_key,
            'created_at': datetime.now().isoformat(),
            'bills': [],
            'documents': [],
            'vectorstore': None,
            'conversation_chain': None,
            'retriever': None,
            'llm': None,
            'chat_history': []
        }
        
        return jsonify({
            'session_id': session_id,
            'created_at': sessions[session_id]['created_at'],
            'message': 'Session created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/upload', methods=['POST'])
def upload_bills():
    """
    Upload and process bills
    
    Form data:
    - session_id: Session ID from create_session
    - files: Multiple bill files (PDF or images)
    
    Response:
    {
        "session_id": "uuid",
        "processed_count": 3,
        "bills": [...],
        "message": "Bills processed successfully"
    }
    """
    try:
        # Get session ID
        session_id = request.form.get('session_id')
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        session = sessions[session_id]
        
        # Check if files are present
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected'}), 400
        
        # Process each file
        processor = BillProcessor()
        processed_bills = []
        documents = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Save file
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
                file.save(filepath)
                
                # Extract text
                extracted_text = processor.extract_text(filepath)
                
                # Extract bill information
                bill_data = processor.extract_bill_info(extracted_text, filename)
                processed_bills.append(bill_data)
                
                # Add to documents for RAG
                documents.append(f"Bill: {filename}\n{extracted_text}")
                
                # Clean up file
                os.remove(filepath)
        
        # Update session
        session['bills'].extend(processed_bills)
        session['documents'].extend(documents)
        
        # Create/update vectorstore and conversation chain
        session['vectorstore'] = create_vectorstore(session['documents'], session['api_key'])
        
        # Initialize LLM if not already done
        if not session['llm']:
            session['llm'] = initialize_openrouter_client(session['api_key'])
        
        chain, retriever = create_conversation_chain(
            session['vectorstore'], 
            session['llm']
        )
        session['conversation_chain'] = chain
        session['retriever'] = retriever
        
        return jsonify({
            'session_id': session_id,
            'processed_count': len(processed_bills),
            'bills': processed_bills,
            'message': f'Successfully processed {len(processed_bills)} bills'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search_bills():
    """
    Search bills using semantic search
    
    Request body:
    {
        "session_id": "uuid",
        "query": "How much did I spend on groceries?",
        "top_k": 5
    }
    
    Response:
    {
        "query": "How much did I spend on groceries?",
        "results": [...],
        "count": 3
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        query = data.get('query')
        top_k = data.get('top_k', 5)
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        session = sessions[session_id]
        
        if not session['vectorstore']:
            return jsonify({'error': 'No bills uploaded yet'}), 400
        
        # Perform similarity search
        results = session['vectorstore'].similarity_search(query, k=top_k)
        
        # Format results
        formatted_results = [
            {
                'content': doc.page_content,
                'metadata': doc.metadata
            }
            for doc in results
        ]
        
        return jsonify({
            'query': query,
            'results': formatted_results,
            'count': len(formatted_results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat with AI about bills
    
    Request body:
    {
        "session_id": "uuid",
        "message": "How can I save money on dining?"
    }
    
    Response:
    {
        "session_id": "uuid",
        "user_message": "How can I save money on dining?",
        "ai_response": "Here are some tips...",
        "sources": [...]
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message')
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        session = sessions[session_id]
        
        if not session['conversation_chain']:
            return jsonify({'error': 'No bills uploaded yet'}), 400
        
        # Format chat history
        chat_history_str = format_chat_history(session['chat_history'])
        
        # Get response from conversation chain
        ai_response = session['conversation_chain'].invoke({
            'question': message,
            'chat_history': chat_history_str
        })
        
        # Store chat history
        session['chat_history'].append({
            'user': message,
            'assistant': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get relevant sources for transparency
        sources = []
        if session['retriever']:
            relevant_docs = session['retriever'].get_relevant_documents(message)
            for doc in relevant_docs[:3]:  # Top 3 sources
                sources.append({
                    'content': doc.page_content[:200] + '...' if len(doc.page_content) > 200 else doc.page_content,
                    'metadata': doc.metadata
                })
        
        return jsonify({
            'session_id': session_id,
            'user_message': message,
            'ai_response': ai_response,
            'sources': sources,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analysis/<session_id>', methods=['GET'])
def get_analysis(session_id):
    """
    Get comprehensive financial analysis
    
    Response:
    {
        "session_id": "uuid",
        "total_spent": 1234.56,
        "total_bills": 15,
        "category_breakdown": {...},
        "insights": {...},
        "recommendations": [...]
    }
    """
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        session = sessions[session_id]
        bills = session['bills']
        
        if not bills:
            return jsonify({'error': 'No bills to analyze'}), 400
        
        # Calculate statistics
        total_spent = sum(bill.get('amount', 0) for bill in bills)
        
        # Category breakdown
        category_breakdown = {}
        for bill in bills:
            category = bill.get('category', 'Other')
            amount = bill.get('amount', 0)
            category_breakdown[category] = category_breakdown.get(category, 0) + amount
        
        # Generate insights
        analysis_engine = AnalysisEngine()
        insights = analysis_engine.generate_insights(bills, session['api_key'])
        
        return jsonify({
            'session_id': session_id,
            'total_spent': round(total_spent, 2),
            'total_bills': len(bills),
            'average_bill': round(total_spent / len(bills), 2) if bills else 0,
            'category_breakdown': category_breakdown,
            'insights': insights,
            'generated_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/bills/<session_id>', methods=['GET'])
def get_bills(session_id):
    """
    Get all processed bills for a session
    
    Response:
    {
        "session_id": "uuid",
        "bills": [...],
        "count": 10
    }
    """
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        session = sessions[session_id]
        
        return jsonify({
            'session_id': session_id,
            'bills': session['bills'],
            'count': len(session['bills']),
            'retrieved_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>', methods=['GET'])
def get_session_info(session_id):
    """
    Get session information
    
    Response:
    {
        "session_id": "uuid",
        "created_at": "timestamp",
        "bills_count": 10,
        "chat_history_count": 5
    }
    """
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        session = sessions[session_id]
        
        return jsonify({
            'session_id': session_id,
            'created_at': session['created_at'],
            'bills_count': len(session['bills']),
            'chat_history_count': len(session['chat_history']),
            'has_vectorstore': session['vectorstore'] is not None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    Delete a session and all associated data
    
    Response:
    {
        "message": "Session deleted successfully"
    }
    """
    try:
        if session_id not in sessions:
            return jsonify({'error': 'Invalid session ID'}), 400
        
        # Clean up session
        del sessions[session_id]
        
        # Clean up any remaining files
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith(session_id):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        return jsonify({
            'message': 'Session deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(sessions)
    }), 200


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({'error': 'File too large. Maximum size is 16MB'}), 413


if __name__ == '__main__':
    print("🚀 Starting BudgetBuddy RAG API...")
    print("📚 API Documentation available at: http://localhost:5000/")
    print("💡 Create a session first: POST /api/session/create")
    app.run(debug=True, host='0.0.0.0', port=5000)