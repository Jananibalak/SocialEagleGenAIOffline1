# 💰 BudgetBuddy - Complete Full-Stack Solution

**Flask REST API + Streamlit Frontend for AI-Powered Bill Analysis**

A production-ready application that combines the power of RAG (Retrieval-Augmented Generation), OCR, and GPT-4 Mini to provide intelligent financial insights.

## 🌟 What's Included

This is a **complete full-stack solution** with:

1. ✅ **Flask REST API** (Backend) - RESTful API for bill processing
2. ✅ **Streamlit Frontend** (UI) - Beautiful web interface
3. ✅ **RAG System** - FAISS vector database for semantic search
4. ✅ **OCR Support** - Process PDFs and images
5. ✅ **AI Chat** - GPT-4 Mini powered conversations
6. ✅ **Smart Analysis** - Automatic categorization and insights

## 📁 Project Structure

```
bill_analyzer_api/
├── app.py                          # Flask REST API (Backend)
├── streamlit_frontend.py           # Streamlit UI (Frontend)
├── bill_processor.py               # OCR and PDF processing
├── analysis_engine.py              # Financial insights generation
├── test_api.py                     # API testing client
├── requirements.txt                # All dependencies
├── .streamlit/
│   └── secrets.toml               # Streamlit configuration
├── README.md                       # This file
├── API_DOCUMENTATION.md           # Complete API reference
├── DEPLOYMENT_GUIDE.md            # How to run both services
└── BudgetBuddy_API.postman_collection.json  # Postman tests
```

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
# Install Tesseract OCR
sudo apt-get install tesseract-ocr  # Linux
brew install tesseract              # Mac

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Start the Backend (Flask API)

**Terminal 1:**
```bash
python app.py
```

You should see:
```
🚀 Starting BudgetBuddy RAG API...
📚 API Documentation available at: http://localhost:5000/
 * Running on http://0.0.0.0:5000
```

### Step 3: Start the Frontend (Streamlit)

**Terminal 2:**
```bash
streamlit run streamlit_frontend.py
```

Your browser will open to `http://localhost:8501`

### Step 4: Use the Application

1. Get your OpenRouter API key from [openrouter.ai](https://openrouter.ai/keys)
2. Enter it in the Streamlit sidebar
3. Click "Create Session"
4. Upload your bills (PDFs or images)
5. Click "Process Bills"
6. Explore your insights! 🎉

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                  User's Browser                      │
│              http://localhost:8501                   │
└─────────────────────┬────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────┐
│              Streamlit Frontend                      │
│  • Beautiful UI with charts and visualizations       │
│  • File upload interface                             │
│  • Chat interface                                    │
│  • Real-time analysis display                        │
└─────────────────────┬────────────────────────────────┘
                      │ HTTP/REST API Calls
                      ▼
┌──────────────────────────────────────────────────────┐
│                 Flask REST API                       │
│              http://localhost:5000                   │
│  • Session management                                │
│  • File upload endpoints                             │
│  • Search endpoints                                  │
│  • Chat endpoints                                    │
│  • Analysis endpoints                                │
└─────────────────────┬────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌─────────┐ ┌────────────┐
│     OCR      │ │   RAG   │ │  Analysis  │
│  Tesseract   │ │  FAISS  │ │   Engine   │
│              │ │  GPT-4  │ │            │
└──────────────┘ └─────────┘ └────────────┘
```

## ✨ Features

### Frontend (Streamlit)
- 🎨 Beautiful, modern UI with gradient design
- 📊 Interactive charts (pie, bar, metrics)
- 💬 Real-time AI chat interface
- 📁 Drag-and-drop file upload
- 📈 Detailed bill breakdown tables
- 📥 CSV export functionality
- 🔄 Session management
- ⚡ Live API connection status

### Backend (Flask API)
- 🔐 Secure session-based authentication
- 📄 Multi-file upload support
- 🔍 Semantic search with RAG
- 💬 Conversational AI (GPT-4 Mini)
- 📊 Financial analysis generation
- 🗄️ FAISS vector storage
- 🌐 CORS enabled
- 📡 RESTful endpoints

### Processing Engine
- 📄 PDF text extraction
- 🖼️ OCR for images (Tesseract)
- 🏷️ Automatic categorization (10+ categories)
- 💰 Amount extraction
- 📅 Date parsing
- 🏪 Merchant detection
- 📝 Line item extraction

### AI & Analytics
- 🤖 GPT-4 Mini for insights
- 🔍 FAISS vector similarity search
- 💡 Personalized recommendations
- ⚠️ Budget warnings
- 📈 Spending trends
- 🎯 Category analysis

## 📚 Documentation

- **[README.md](README.md)** - This file (Quick start & overview)
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Complete API reference
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Detailed deployment instructions
- **[PYTHON_311_COMPATIBILITY.md](../PYTHON_311_COMPATIBILITY.md)** - Python 3.11 guide

## 🎯 Use Cases

### 1. Personal Finance Management
- Track monthly expenses
- Identify spending patterns
- Get personalized saving tips
- Budget planning

### 2. Small Business Expense Tracking
- Monitor business expenses
- Categorize for tax purposes
- Vendor analysis
- Monthly reports

### 3. Financial Planning
- Prepare for advisor meetings
- Understand spending habits
- Set realistic budgets
- Track progress

### 4. Integration with Other Apps
- Use API in mobile apps
- Connect to accounting software
- Build custom dashboards
- Automate expense processing

## 🔧 Configuration

### Flask API (.env)
```env
FLASK_ENV=development
FLASK_DEBUG=True
OPENROUTER_API_KEY=your_key_here
MAX_FILE_SIZE=16777216
HOST=0.0.0.0
PORT=5000
```

### Streamlit (.streamlit/secrets.toml)
```toml
API_BASE_URL = "http://localhost:5000"
```

## 🧪 Testing

### Test the API Directly
```bash
python test_api.py
```

### Test with Postman
Import `BudgetBuddy_API.postman_collection.json` into Postman

### Test the UI
1. Open browser to `http://localhost:8501`
2. Follow the in-app instructions

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/session/create` | Create new session |
| POST | `/api/upload` | Upload bills |
| POST | `/api/search` | Semantic search |
| POST | `/api/chat` | Chat with AI |
| GET | `/api/analysis/{id}` | Get analysis |
| GET | `/api/bills/{id}` | Get all bills |
| GET | `/api/health` | Health check |

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete details.

## 🖥️ System Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- 1GB disk space
- Tesseract OCR

### Recommended
- Python 3.11+ (best performance)
- 4GB+ RAM
- 2GB+ disk space
- SSD for faster processing

## 🌐 Browser Support

- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

## 🔐 Security

- API keys never stored permanently
- Files deleted after processing
- Session-based isolation
- CORS configured
- Input validation
- Error handling

## 🐛 Troubleshooting

### Common Issues

**1. Cannot connect to API**
```bash
# Make sure Flask API is running
python app.py

# Check API health
curl http://localhost:5000/api/health
```

**2. Port already in use**
```bash
# Kill process on port 5000
lsof -i :5000
kill -9 <PID>

# Or use different port
python app.py  # Edit app.py to change port
```

**3. OCR not working**
```bash
# Install Tesseract
sudo apt-get install tesseract-ocr

# Verify installation
tesseract --version
```

**4. File upload fails**
- Check file size (max 16MB)
- Verify file format (PDF, PNG, JPG, JPEG)
- Ensure Tesseract is installed

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for more troubleshooting.

## 🚀 Production Deployment

### Using Gunicorn + Systemd

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for:
- Systemd service configuration
- Nginx reverse proxy setup
- Docker deployment
- SSL certificate setup
- Performance optimization

### Quick Production Setup
```bash
# Install production server
pip install gunicorn

# Run API with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Run Streamlit (in separate terminal)
streamlit run streamlit_frontend.py
```

## 📊 Performance

- **API Response**: ~100-500ms
- **Bill Processing**: ~2-5 seconds per bill
- **Chat Response**: ~1-3 seconds
- **Search**: <100ms
- **Concurrent Users**: 10+ supported

## 🔄 Updates & Maintenance

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Clear old sessions (if using file storage)
rm -rf uploads/*

# Check for updates
pip list --outdated
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional file format support
- Enhanced categorization rules
- Multi-language support
- Database persistence
- Rate limiting
- Caching layer
- Mobile app

## 📝 License

MIT License - Free to use and modify!

## 🙏 Credits

Built with:
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Streamlit](https://streamlit.io/) - UI framework
- [LangChain](https://langchain.com/) - LLM framework
- [FAISS](https://github.com/facebookresearch/faiss) - Vector search
- [OpenRouter](https://openrouter.ai/) - AI API
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - OCR
- [Plotly](https://plotly.com/) - Visualizations

## 📞 Support

### Getting Help
1. Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Review [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
3. Test with sample bills
4. Check logs for errors

### Useful Commands
```bash
# Check if services are running
curl http://localhost:5000/api/health  # API
curl http://localhost:8501/            # Streamlit

# View processes
ps aux | grep python

# Check logs
tail -f api.log
tail -f streamlit.log
```

## 🎉 Success Checklist

- [ ] Python 3.11 installed
- [ ] Tesseract OCR installed
- [ ] Dependencies installed
- [ ] Flask API running on port 5000
- [ ] Streamlit running on port 8501
- [ ] OpenRouter API key obtained
- [ ] Test bills ready
- [ ] Browser opened to localhost:8501

## 🌟 What's Next?

Once you have it running:
1. Upload some sample bills
2. Explore the AI insights
3. Try the chat feature
4. Export your data
5. Integrate with your apps via API!

---

## 📖 Quick Reference

### Start Both Services
```bash
# Terminal 1
python app.py

# Terminal 2
streamlit run streamlit_frontend.py
```

### Access Points
- **Frontend UI**: http://localhost:8501
- **API**: http://localhost:5000
- **API Docs**: http://localhost:5000/

### Test Files Location
- Upload bills through Streamlit UI
- Or use API: `POST /api/upload`

---

**Made with ❤️ for better financial insights**

**Ready to analyze your bills? Let's go! 🚀💰**
