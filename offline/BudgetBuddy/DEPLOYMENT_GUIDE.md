# 🚀 Complete Deployment Guide - Flask API + Streamlit Frontend

This guide covers running both the Flask REST API backend and Streamlit frontend together.

## 📋 Overview

The system consists of two parts:
1. **Flask API** (Backend) - Runs on `http://localhost:5000`
2. **Streamlit Frontend** (UI) - Runs on `http://localhost:8501`

```
┌─────────────────┐
│   Streamlit     │  (Port 8501)
│    Frontend     │
└────────┬────────┘
         │ HTTP Requests
         ▼
┌─────────────────┐
│   Flask API     │  (Port 5000)
│    Backend      │
└────────┬────────┘
         │
         ├─► Bill Processor (OCR/PDF)
         ├─► Analysis Engine
         └─► RAG System (FAISS + GPT-4)
```

## 🏁 Quick Start (Both Services)

### Option 1: Run Both in Same Terminal (Recommended for Testing)

```bash
# Terminal 1: Start Flask API
cd bill_analyzer_api
python app.py

# Terminal 2: Start Streamlit Frontend
cd bill_analyzer_api
streamlit run streamlit_frontend.py
```

### Option 2: Background Services (Linux/Mac)

```bash
# Start Flask API in background
cd bill_analyzer_api
nohup python app.py > api.log 2>&1 &

# Start Streamlit in background
nohup streamlit run streamlit_frontend.py > streamlit.log 2>&1 &

# Check logs
tail -f api.log
tail -f streamlit.log
```

### Option 3: Using tmux (Recommended for Development)

```bash
# Create new tmux session
tmux new -s budgetbuddy

# Split window horizontally (Ctrl+b, then ")
# Top pane: Flask API
cd bill_analyzer_api && python app.py

# Switch to bottom pane (Ctrl+b, then down arrow)
# Bottom pane: Streamlit
cd bill_analyzer_api && streamlit run streamlit_frontend.py

# Detach from tmux: Ctrl+b, then d
# Reattach: tmux attach -t budgetbuddy
```

## 📦 Prerequisites

### 1. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

### 2. Install Python Dependencies

```bash
cd bill_analyzer_api
pip install -r requirements.txt

# Also need Streamlit (if not in requirements)
pip install streamlit==1.31.0
```

### 3. Get OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Sign up or log in
3. Create a new API key
4. Save it for later use

## 🔧 Configuration

### Flask API Configuration

Create `.env` file:

```env
FLASK_ENV=development
FLASK_DEBUG=True
OPENROUTER_API_KEY=your_key_here  # Optional
MAX_FILE_SIZE=16777216
HOST=0.0.0.0
PORT=5000
```

### Streamlit Configuration

Create `.streamlit/secrets.toml`:

```toml
API_BASE_URL = "http://localhost:5000"
```

## 🚀 Step-by-Step Deployment

### Step 1: Start the Flask API

```bash
cd bill_analyzer_api
python app.py
```

You should see:
```
🚀 Starting BudgetBuddy RAG API...
📚 API Documentation available at: http://localhost:5000/
💡 Create a session first: POST /api/session/create
 * Running on http://0.0.0.0:5000
```

**Verify API is running:**
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "active_sessions": 0
}
```

### Step 2: Start the Streamlit Frontend

In a **new terminal**:

```bash
cd bill_analyzer_api
streamlit run streamlit_frontend.py
```

You should see:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

Your browser should automatically open to `http://localhost:8501`

### Step 3: Use the Application

1. **Enter API Key** in the sidebar
2. **Click "Create Session"**
3. **Upload bills** (PDFs or images)
4. **Click "Process Bills"**
5. **Explore insights** in different tabs!

## 📱 Using the Application

### Overview Tab (📊)
- See total spending metrics
- View pie and bar charts
- Understand category breakdown

### AI Insights Tab (🔥)
- Read personalized observations
- Get budget warnings
- Receive saving recommendations

### Chat Tab (💬)
- Ask questions about your bills
- Get AI-powered responses
- View source citations

### Bill Details Tab (📈)
- See all bills in a table
- Download as CSV
- Expand for detailed view

## 🧪 Testing the Integration

### Test 1: API Connection

In the Streamlit app, you should see:
- ✅ Green checkmark if API is running
- ❌ Red error if API is down

### Test 2: Upload and Process

1. Upload a sample bill
2. Should see: "✅ Processed 1 bills!"
3. Analysis should load automatically

### Test 3: Chat Functionality

Ask: "How much did I spend total?"

Should get a response like:
"You've spent $123.45 across 3 bills! 💰"

## 🐛 Troubleshooting

### Issue 1: Cannot Connect to API

**Symptom:** Red error message "Cannot connect to API"

**Solutions:**
```bash
# Check if API is running
curl http://localhost:5000/api/health

# If not, start it
cd bill_analyzer_api
python app.py

# Check for port conflicts
lsof -i :5000  # Kill any process using port 5000
```

### Issue 2: Streamlit Won't Start

**Symptom:** Port 8501 already in use

**Solutions:**
```bash
# Find process using port 8501
lsof -i :8501

# Kill it
kill -9 <PID>

# Or use a different port
streamlit run streamlit_frontend.py --server.port 8502
```

### Issue 3: File Upload Fails

**Symptom:** Upload error or timeout

**Solutions:**
- Check file size (max 16MB)
- Verify file format (PDF, PNG, JPG, JPEG)
- Check API logs for errors
- Ensure Tesseract is installed

### Issue 4: OCR Not Working

**Symptom:** Text extraction fails

**Solutions:**
```bash
# Verify Tesseract installation
tesseract --version

# If not installed
sudo apt-get install tesseract-ocr  # Linux
brew install tesseract              # Mac
```

### Issue 5: Chat Returns Errors

**Symptom:** Chat fails or gives errors

**Solutions:**
- Verify API key is valid
- Check OpenRouter credits
- Ensure bills were uploaded first
- Check API logs for details

## 📊 Monitoring

### View Logs

**Flask API Logs:**
```bash
# If running in foreground, logs show in terminal

# If using nohup
tail -f api.log

# If using systemd
journalctl -u budgetbuddy-api -f
```

**Streamlit Logs:**
```bash
# If running in foreground, logs show in terminal

# If using nohup
tail -f streamlit.log
```

### Check Active Sessions

```bash
curl http://localhost:5000/api/health
```

Response shows `active_sessions` count.

## 🔄 Restarting Services

### Restart Flask API

```bash
# Find and kill process
pkill -f "python app.py"

# Or if you know the PID
kill <PID>

# Restart
python app.py
```

### Restart Streamlit

```bash
# Find and kill process
pkill -f "streamlit run"

# Restart
streamlit run streamlit_frontend.py
```

## 🚀 Production Deployment

### Using Gunicorn for Flask

```bash
# Install gunicorn
pip install gunicorn

# Run Flask with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# With more workers
gunicorn -w 8 -b 0.0.0.0:5000 --timeout 120 app:app
```

### Using Systemd (Linux)

**Flask API Service:**

Create `/etc/systemd/system/budgetbuddy-api.service`:

```ini
[Unit]
Description=BudgetBuddy Flask API
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/bill_analyzer_api
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

**Streamlit Service:**

Create `/etc/systemd/system/budgetbuddy-frontend.service`:

```ini
[Unit]
Description=BudgetBuddy Streamlit Frontend
After=network.target

[Service]
User=your_user
WorkingDirectory=/path/to/bill_analyzer_api
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/streamlit run streamlit_frontend.py --server.port 8501

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**

```bash
sudo systemctl enable budgetbuddy-api
sudo systemctl enable budgetbuddy-frontend
sudo systemctl start budgetbuddy-api
sudo systemctl start budgetbuddy-frontend

# Check status
sudo systemctl status budgetbuddy-api
sudo systemctl status budgetbuddy-frontend
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped

  frontend:
    build: .
    command: streamlit run streamlit_frontend.py --server.port 8501
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://api:5000
    depends_on:
      - api
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## 🌐 Nginx Reverse Proxy

Create `/etc/nginx/sites-available/budgetbuddy`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Streamlit frontend
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Flask API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/budgetbuddy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔒 Security Considerations

### Production Checklist

- [ ] Use environment variables for secrets
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up firewall rules
- [ ] Use strong API keys
- [ ] Implement rate limiting
- [ ] Add authentication (if multi-user)
- [ ] Regular security updates
- [ ] Backup uploaded bills
- [ ] Monitor logs for suspicious activity

### Securing API Keys

Never commit API keys to git:

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo ".streamlit/secrets.toml" >> .gitignore
echo "uploads/" >> .gitignore
```

## 💡 Tips

1. **Development:**
   - Use tmux for easy terminal management
   - Enable debug mode for detailed errors
   - Monitor logs in real-time

2. **Testing:**
   - Test with sample bills first
   - Use Postman for API testing
   - Check network tab in browser for errors

3. **Performance:**
   - Increase Gunicorn workers for more traffic
   - Use Redis for session storage in production
   - Compress images before uploading

4. **Maintenance:**
   - Regularly update dependencies
   - Clean up old sessions
   - Monitor disk space for uploads
   - Rotate logs

## 📚 Useful Commands

```bash
# Check if services are running
curl http://localhost:5000/api/health  # API
curl http://localhost:8501/            # Streamlit

# View running Python processes
ps aux | grep python

# Check ports
lsof -i :5000
lsof -i :8501

# Kill all Python processes (careful!)
pkill -f python

# Monitor resource usage
htop
```

## 🎉 Success!

If everything is working, you should be able to:
- ✅ Access Streamlit at http://localhost:8501
- ✅ See green API status indicator
- ✅ Upload and process bills
- ✅ View beautiful visualizations
- ✅ Chat with AI about your spending

---

**Happy budgeting! 💰✨**

For issues, check the troubleshooting section or review the logs.
