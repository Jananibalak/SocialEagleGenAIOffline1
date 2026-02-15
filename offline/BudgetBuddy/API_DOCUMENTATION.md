# 🚀 BudgetBuddy RAG API Documentation

A RESTful API for bill analysis and financial insights using RAG (Retrieval-Augmented Generation).

## 📋 Table of Contents
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Request/Response Examples](#examples)
- [Error Handling](#error-handling)
- [Client Libraries](#client-libraries)

## 🏁 Getting Started

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (for image processing)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# Windows:
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Running the API

```bash
python app.py
```

The API will start on `http://localhost:5000`

## 🔐 Authentication

The API uses OpenRouter API keys for authentication. You need to:
1. Get an API key from [OpenRouter](https://openrouter.ai/keys)
2. Include it when creating a session

## 📡 API Endpoints

### Base URL
```
http://localhost:5000
```

---

### 1. Home / API Info

**GET /** 

Get API information and available endpoints.

**Response:**
```json
{
  "name": "BudgetBuddy RAG API",
  "version": "1.0.0",
  "description": "AI-powered bill analysis and financial insights API",
  "endpoints": {...},
  "status": "running"
}
```

---

### 2. Create Session

**POST /api/session/create**

Create a new session for bill analysis.

**Request Body:**
```json
{
  "api_key": "your_openrouter_api_key"
}
```

**Response (201):**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2024-01-15T10:30:00",
  "message": "Session created successfully"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/session/create \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your_api_key_here"}'
```

---

### 3. Upload Bills

**POST /api/upload**

Upload and process bills (PDF or images).

**Form Data:**
- `session_id`: String (required)
- `files`: File[] (required) - Multiple files supported

**Response (200):**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "processed_count": 3,
  "bills": [
    {
      "filename": "walmart_receipt.pdf",
      "merchant": "WALMART SUPERCENTER",
      "amount": 45.67,
      "date": "01/15/2024",
      "category": "Groceries",
      "items": [...]
    }
  ],
  "message": "Successfully processed 3 bills"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "session_id=your_session_id" \
  -F "files=@bill1.pdf" \
  -F "files=@bill2.jpg"
```

**Python Example:**
```python
import requests

files = [
    ('files', open('bill1.pdf', 'rb')),
    ('files', open('bill2.jpg', 'rb'))
]
data = {'session_id': 'your_session_id'}

response = requests.post(
    'http://localhost:5000/api/upload',
    data=data,
    files=files
)
```

---

### 4. Search Bills

**POST /api/search**

Search bills using semantic search (RAG).

**Request Body:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "query": "How much did I spend on groceries?",
  "top_k": 5
}
```

**Response (200):**
```json
{
  "query": "How much did I spend on groceries?",
  "results": [
    {
      "content": "Bill: walmart_receipt.pdf\nWALMART SUPERCENTER...",
      "metadata": {}
    }
  ],
  "count": 3
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "query": "How much did I spend on groceries?",
    "top_k": 5
  }'
```

---

### 5. Chat with AI

**POST /api/chat**

Have a conversation with the AI about your bills.

**Request Body:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "How can I save money on dining?"
}
```

**Response (200):**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_message": "How can I save money on dining?",
  "ai_response": "🍽️ Great question! I noticed you spent $450 on dining this month...",
  "sources": [
    {
      "content": "Bill: restaurant_receipt.pdf...",
      "metadata": {}
    }
  ],
  "timestamp": "2024-01-15T10:35:00"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "message": "How can I save money on dining?"
  }'
```

---

### 6. Get Analysis

**GET /api/analysis/{session_id}**

Get comprehensive financial analysis.

**Response (200):**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "total_spent": 1234.56,
  "total_bills": 15,
  "average_bill": 82.30,
  "category_breakdown": {
    "Groceries": 450.00,
    "Dining": 350.00,
    "Utilities": 200.00
  },
  "insights": {
    "observations": "📊 You've spent $1,234.56 across 15 bills...",
    "warnings": "⚠️ Dining: You're $50 over budget...",
    "recommendations": "💡 Try meal prepping..."
  },
  "generated_at": "2024-01-15T10:40:00"
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/analysis/your_session_id
```

---

### 7. Get All Bills

**GET /api/bills/{session_id}**

Get all processed bills for a session.

**Response (200):**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "bills": [
    {
      "filename": "walmart_receipt.pdf",
      "merchant": "WALMART SUPERCENTER",
      "amount": 45.67,
      "date": "01/15/2024",
      "category": "Groceries",
      "items": [...]
    }
  ],
  "count": 10,
  "retrieved_at": "2024-01-15T10:45:00"
}
```

---

### 8. Get Session Info

**GET /api/session/{session_id}**

Get session information.

**Response (200):**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2024-01-15T10:30:00",
  "bills_count": 10,
  "chat_history_count": 5,
  "has_vectorstore": true
}
```

---

### 9. Delete Session

**DELETE /api/session/{session_id}**

Delete a session and all associated data.

**Response (200):**
```json
{
  "message": "Session deleted successfully"
}
```

**cURL Example:**
```bash
curl -X DELETE http://localhost:5000/api/session/your_session_id
```

---

### 10. Health Check

**GET /api/health**

Check API health status.

**Response (200):**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:50:00",
  "active_sessions": 3
}
```

---

## 🔄 Complete Workflow Example

### 1. Create Session
```python
import requests

# Create session
response = requests.post('http://localhost:5000/api/session/create', 
    json={'api_key': 'your_api_key'})
session_id = response.json()['session_id']
```

### 2. Upload Bills
```python
# Upload bills
files = [
    ('files', open('bill1.pdf', 'rb')),
    ('files', open('bill2.jpg', 'rb'))
]
response = requests.post('http://localhost:5000/api/upload',
    data={'session_id': session_id},
    files=files)
```

### 3. Get Analysis
```python
# Get analysis
response = requests.get(f'http://localhost:5000/api/analysis/{session_id}')
analysis = response.json()
print(f"Total Spent: ${analysis['total_spent']:.2f}")
```

### 4. Chat with AI
```python
# Chat
response = requests.post('http://localhost:5000/api/chat',
    json={
        'session_id': session_id,
        'message': 'How can I reduce my expenses?'
    })
print(response.json()['ai_response'])
```

### 5. Search Bills
```python
# Search
response = requests.post('http://localhost:5000/api/search',
    json={
        'session_id': session_id,
        'query': 'grocery bills',
        'top_k': 5
    })
```

### 6. Clean Up
```python
# Delete session
requests.delete(f'http://localhost:5000/api/session/{session_id}')
```

---

## ❌ Error Handling

### Common Error Codes

| Code | Meaning | Example Response |
|------|---------|------------------|
| 400 | Bad Request | `{"error": "API key is required"}` |
| 404 | Not Found | `{"error": "Endpoint not found"}` |
| 413 | Payload Too Large | `{"error": "File too large. Maximum size is 16MB"}` |
| 500 | Internal Server Error | `{"error": "Internal server error"}` |

### Error Response Format
```json
{
  "error": "Description of the error"
}
```

---

## 📚 Client Libraries

### Python Client

Use the included `test_api.py` as a reference:

```python
from test_api import BudgetBuddyClient

client = BudgetBuddyClient('http://localhost:5000', 'your_api_key')
client.create_session()
client.upload_bills(['bill1.pdf', 'bill2.jpg'])
client.get_analysis()
client.chat("How can I save money?")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');
const FormData = require('form-data');

// Create session
const session = await axios.post('http://localhost:5000/api/session/create', {
  api_key: 'your_api_key'
});
const sessionId = session.data.session_id;

// Upload bills
const form = new FormData();
form.append('session_id', sessionId);
form.append('files', fs.createReadStream('bill1.pdf'));

await axios.post('http://localhost:5000/api/upload', form, {
  headers: form.getHeaders()
});

// Get analysis
const analysis = await axios.get(`http://localhost:5000/api/analysis/${sessionId}`);
console.log(analysis.data);
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
FLASK_ENV=development
FLASK_DEBUG=True
MAX_FILE_SIZE=16777216  # 16MB in bytes
UPLOAD_FOLDER=uploads
```

### File Upload Limits

- Maximum file size: 16MB
- Supported formats: PDF, PNG, JPG, JPEG
- Multiple files: Yes

---

## 🚀 Deployment Tips

### Production Considerations

1. **Use a production WSGI server:**
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Add Redis for session storage:**
```python
# Instead of in-memory sessions dict
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
```

3. **Add rate limiting:**
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=get_remote_address)
```

4. **Use environment variables for secrets:**
```python
import os
api_key = os.getenv('OPENROUTER_API_KEY')
```

---

## 📝 Notes

- Sessions are stored in memory by default (not persistent)
- For production, use Redis or a database for session storage
- Files are temporarily stored during processing then deleted
- API supports CORS for cross-origin requests

---

## 💡 Tips

1. **Batch Upload**: Upload multiple bills at once for efficiency
2. **Session Management**: Clean up sessions when done to free memory
3. **Error Handling**: Always check response status codes
4. **File Size**: Compress large images before uploading
5. **Rate Limits**: OpenRouter has rate limits - be mindful

---

## 🐛 Troubleshooting

**Session Not Found:**
- Ensure you created a session first
- Session IDs are UUIDs - copy them exactly

**Upload Failed:**
- Check file size (max 16MB)
- Verify file format is supported
- Ensure Tesseract is installed for images

**OCR Not Working:**
- Install Tesseract OCR
- Use clear, well-lit images
- Try PDF format instead

**Chat Not Responding:**
- Verify API key is valid
- Check OpenRouter credits
- Ensure bills were uploaded successfully

---

## 📞 Support

For issues or questions:
- Check this documentation
- Review the test_api.py examples
- Verify API is running: `GET /api/health`

---

Made with ❤️ for better financial insights!
