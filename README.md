# 📄🔍 Document Q&A RAG Demo

A production-ready **Retrieval-Augmented Generation (RAG)** chatbot for intelligent document Q&A, designed for enterprise clients. Built with Python 3.11, LangChain, Streamlit, FAISS, and OpenAI GPT-4o.

## 🚀 Features

### Core Functionality
- **Multi-file Upload**: Support for PDF, DOCX, and TXT files
- **Intelligent Chunking**: 1KB chunks with overlap for optimal retrieval
- **Vector Storage**: FAISS for fast, privacy-focused local vector storage
- **RAG Pipeline**: Retrieval-Augmented Generation with strict context control
- **Source Citations**: Show exact document snippets with page/file references
- **Real-time Processing**: Display response time and token usage

### User Interface
- **Streamlit Web App**: Modern, responsive interface
- **Sidebar Upload**: Drag-and-drop file upload zone
- **Chat Interface**: Conversational Q&A with history
- **Expandable Sources**: Collapsible source documentation panel
- **Live Statistics**: Token usage, response times, document stats

### Configuration
- **Environment Variables**: Secure configuration via `.env` file
- **Strict Mode Toggle**: Control answer generation strictness
- **Customizable Parameters**: Chunk size, overlap, retrieval count

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Document Q&A RAG System                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Streamlit  │    │   LangChain │    │   OpenAI    │     │
│  │     UI      │◄──►│  RAG Chain  │◄──►│   GPT-4o    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                              │
│         ▼                   ▼                              │
│  ┌─────────────┐    ┌─────────────┐                       │
│  │   Document  │    │    FAISS    │                       │
│  │   Loader    │──► │  Vector DB  │                       │
│  └─────────────┘    └─────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Data Flow:
1. User uploads documents (PDF/DOCX/TXT)
2. DocumentLoader extracts and chunks text
3. FAISS creates embeddings and stores vectors
4. User asks questions via Streamlit interface
5. QAChain retrieves relevant chunks
6. GPT-4o generates answers based on context
7. UI displays answer with source citations
```

## 📦 Installation

### Prerequisites
- Python 3.11+
- OpenAI API key
- Git

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd rag
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your OpenAI API key
   ```

5. **Run the application**
   ```bash
   streamlit run app/ui.py
   ```

The application will open in your browser at `http://localhost:8501`

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# RAG System Settings
STRICT_MODE=True          # Only answer from retrieved context
CHUNK_SIZE=1000          # Text chunk size (bytes)
CHUNK_OVERLAP=200        # Overlap between chunks
MAX_TOKENS=2000          # Maximum response tokens
TEMPERATURE=0            # Response creativity (0-2)
MODEL_NAME=gpt-4o        # OpenAI model

# Vector Database
VECTOR_DB_PATH=./vector_db  # Local storage path
TOP_K_RESULTS=5            # Number of chunks to retrieve

# UI Customization
PAGE_TITLE=Document Q&A RAG Demo
PAGE_ICON=📄🔍
```

### Key Configuration Options

- **STRICT_MODE**: When `True`, answers are limited to retrieved context only
- **CHUNK_SIZE**: Larger chunks provide more context but may reduce precision
- **TOP_K_RESULTS**: More results provide better coverage but increase costs
- **TEMPERATURE**: 0 for deterministic, higher for creative responses

## 📁 Project Structure

```
rag/
├── app/
│   ├── __init__.py      # Package initialization
│   ├── loader.py        # Document parsing & chunking
│   ├── vectordb.py      # FAISS vector storage manager
│   ├── qa_chain.py      # LangChain RAG pipeline
│   ├── ui.py           # Streamlit frontend
│   └── utils.py        # Utility functions & helpers
├── requirements.txt     # Python dependencies
├── .env.example        # Configuration template
├── README.md          # This file
└── vector_db/         # Generated vector database (git-ignored)
```

## 🔧 Usage

### 1. Upload Documents
- Use the sidebar to upload PDF, DOCX, or TXT files
- Multiple files supported simultaneously
- Files are processed and chunked automatically

### 2. Build Vector Database
- Click "Rebuild Vector DB" after uploading files
- Watch processing time and chunk statistics
- Database persists between sessions

### 3. Ask Questions
- Type questions in the chat interface
- Receive answers with source citations
- View token usage and response times

### 4. Review Sources
- Expand "View Sources" for each answer
- See exact text snippets used
- Navigate to specific pages/files

## 🚀 Deployment

### Option 1: Streamlit Community Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial RAG system"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set `app/ui.py` as the main file
   - Add secrets in Streamlit dashboard

3. **Configure Secrets**
   ```toml
   # .streamlit/secrets.toml
   OPENAI_API_KEY = "your_key_here"
   ```

### Option 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app/ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **Build and run**
   ```bash
   docker build -t rag-app .
   docker run -p 8501:8501 --env-file .env rag-app
   ```

### Option 3: Production Server

1. **Install production dependencies**
   ```bash
   pip install gunicorn
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app.ui:app
   ```

## 🧪 Development

### Adding New Document Types

1. **Extend DocumentLoader** (`app/loader.py`)
   ```python
   def load_your_format(self, file_path: str):
       # Implementation for new format
       pass
   ```

2. **Update file upload types** (`app/ui.py`)
   ```python
   uploaded_files = st.file_uploader(
       type=['pdf', 'docx', 'txt', 'your_format']
   )
   ```

### Custom Prompt Templates

Modify `app/qa_chain.py` to customize the prompt:

```python
template = """Custom prompt template here...
Context: {context}
Question: {question}
Answer:"""
```

### Alternative LLM Integration

Replace OpenAI with local models:

```python
# Example: Ollama integration
from langchain.llms import Ollama
llm = Ollama(model="llama2")
```

## 📊 Performance Optimization

### Vector Database
- **FAISS**: Optimized for similarity search
- **Persistence**: Database saves to disk automatically
- **Memory**: Loads into RAM for fast queries

### Chunking Strategy
- **Recursive splitting**: Preserves document structure
- **Overlap**: Ensures context continuity
- **Size optimization**: 1KB chunks balance context vs. precision

### Caching
- **Streamlit caching**: UI state persistence
- **Vector caching**: Embeddings stored locally
- **Session management**: Chat history maintained

## 🔒 Security Considerations

### API Keys
- Store in environment variables
- Never commit to version control
- Use secret management in production

### Data Privacy
- FAISS stores vectors locally
- No data sent to external services (except OpenAI)
- Documents processed in memory only

### Access Control
- Add authentication for production
- Implement rate limiting
- Monitor API usage

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   ```bash
   # Verify your .env file
   cat .env
   # Check API key validity
   ```

2. **Memory Issues with Large Files**
   ```python
   # Reduce chunk size
   CHUNK_SIZE=500
   # Process files individually
   ```

3. **Slow Vector Search**
   ```python
   # Reduce retrieval count
   TOP_K_RESULTS=3
   # Rebuild with smaller chunks
   ```

### Debug Mode

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Monitoring & Analytics

### Built-in Metrics
- Response times per query
- Token usage tracking
- Document processing statistics
- User interaction logs

### Custom Analytics

Add your own tracking:

```python
# In app/utils.py
def track_usage(query, response_time, tokens):
    # Your analytics implementation
    pass
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain**: RAG framework and document processing
- **OpenAI**: GPT-4o language model
- **FAISS**: Efficient similarity search
- **Streamlit**: Web application framework
- **PyMuPDF**: PDF processing capabilities

## 📞 Support

For enterprise support and custom implementations:
- 📧 Email: your-email@domain.com
- 💼 LinkedIn: your-linkedin-profile
- 🐛 Issues: GitHub Issues tab

---

**Built with ❤️ for intelligent document processing** 