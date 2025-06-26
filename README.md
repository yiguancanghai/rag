# 🔧 IntelliDocs Pro - Enterprise Document Q&A System

IntelliDocs Pro is an intelligent document question-answering system built with RAG (Retrieval-Augmented Generation) technology. Upload your documents and ask questions in natural language to get accurate, contextual answers with source citations.

## 🌟 Features

### Core Functionality
- **Multi-format Document Support**: PDF, Word, PowerPoint, Excel, Markdown, and text files
- **Intelligent Q&A**: Natural language queries with contextual understanding
- **Source Attribution**: Every answer includes citations with document sources
- **Multi-turn Conversations**: Context-aware chat sessions
- **Document Management**: Upload, organize, and manage your document collection

### Advanced Features
- **Confidence Scoring**: AI-powered answer confidence assessment
- **Favorites System**: Save important Q&A pairs for easy reference
- **Analytics Dashboard**: Track usage patterns and document statistics
- **Streaming Responses**: Real-time answer generation
- **Search History**: Find previous conversations and answers

### User Experience
- **Modern Web Interface**: Built with Streamlit for responsive design
- **Drag & Drop Upload**: Easy document uploading with progress tracking
- **Customizable Settings**: Adjust retrieval parameters and AI behavior
- **Export Capabilities**: Save conversations and favorites

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd intellidocs-pro
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   
   **Option 1: Use existing environment variable (recommended if already set in zsh)**
   ```bash
   echo $OPENAI_API_KEY  # Verify your API key is set
   ```
   
   **Option 2: Use .env file**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env and add your OpenAI API key
   ```

4. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

5. **Open in browser**
   - Navigate to `http://localhost:8501`
   - Upload documents and start asking questions!

## 📖 Usage Guide

### 1. Document Upload
1. Navigate to "Document Management" in the sidebar
2. Upload your documents (PDF, Word, PowerPoint, Excel, etc.)
3. Configure chunk size and overlap if needed
4. Click "Process Documents" to add them to the knowledge base

### 2. Ask Questions
1. Go to the "Chat" section
2. Type your question in natural language
3. Get answers with source citations and confidence scores
4. Continue the conversation for follow-up questions

### 3. Manage Favorites
1. Click the ⭐ button next to helpful answers
2. Access saved Q&A pairs in the "Favorites" section
3. Organize and reference important information

### 4. Analytics
1. View document and usage statistics in "Analytics"
2. Track conversation patterns and system performance
3. Monitor document collection growth

## 🏗️ Architecture

### Technology Stack
- **Frontend**: Streamlit (Web UI)
- **Backend**: Python, FastAPI-ready architecture
- **LLM**: OpenAI GPT-4 (configurable)
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Database**: ChromaDB (persistent storage)
- **Document Processing**: LangChain + Unstructured

### Project Structure
```
intellidocs-pro/
├── app/
│   ├── main.py                 # Streamlit application entry point
│   ├── core/
│   │   ├── document_processor.py # Document upload and processing
│   │   ├── rag_engine.py        # RAG implementation
│   │   └── chat_manager.py      # Conversation management
│   ├── ui/
│   │   └── components/          # UI components
│   └── utils/
│       ├── config.py           # Configuration management
│       └── logger.py           # Logging utilities
├── data/
│   ├── documents/              # Uploaded documents
│   └── vector_db/             # ChromaDB storage
├── config/
│   └── .env.example           # Environment configuration template
└── requirements.txt           # Python dependencies
```

## ⚙️ Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
CHUNK_SIZE=1000                # Text chunk size for processing
CHUNK_OVERLAP=200             # Overlap between chunks
TEMPERATURE=0.1               # LLM temperature (0.0-1.0)
MAX_TOKENS=2000              # Maximum response length
MAX_UPLOAD_SIZE_MB=100       # Maximum file upload size
```

### Customization Options
- **Retrieval Settings**: Adjust number of documents retrieved per query
- **Response Style**: Control AI creativity and focus
- **Processing Parameters**: Fine-tune document chunking
- **UI Preferences**: Toggle source display and confidence scores

## 🔧 Advanced Features

### Multi-LLM Support
The system is designed to support multiple LLM providers:
- OpenAI GPT-4 (default)
- Anthropic Claude (configurable)
- Local models via Ollama (optional)

### Custom Document Processors
Extend support for additional file formats by implementing custom loaders in the `DocumentProcessor` class.

### API Integration
The core components are API-ready for integration with other systems or building custom interfaces.

## 📊 Performance

### Supported Scale
- **Documents**: Tested with 1000+ documents
- **File Size**: Up to 100MB per file
- **Concurrent Users**: Optimized for small team usage
- **Response Time**: Typically 2-5 seconds per query

### Optimization Tips
- Use appropriate chunk sizes for your document types
- Adjust retrieval parameters based on your use case
- Monitor vector database size and performance
- Consider document preprocessing for better accuracy

## 🚨 Troubleshooting

### Common Issues

**1. API Key Errors**
- Ensure your OpenAI API key is correctly set
- Check API key permissions and billing status

**2. Document Processing Failures**
- Verify file format is supported
- Check file size limits
- Ensure documents are not corrupted

**3. Slow Response Times**
- Reduce number of retrieved documents
- Optimize chunk size settings
- Check internet connection

**4. Memory Issues**
- Monitor system RAM usage
- Clear document collection if needed
- Restart the application

### Support
For issues and feature requests, please check the troubleshooting guide or create an issue in the project repository.

## 🔐 Security Notes

- API keys are stored locally in environment variables
- Documents are processed and stored locally
- No data is sent to external services except for LLM API calls
- Consider additional security measures for production deployment

## 🤝 Contributing

Contributions are welcome! Areas for improvement include:
- Additional document format support
- Enhanced UI/UX features
- Performance optimizations
- Security enhancements
- Test coverage expansion

## 📄 License

This project is open source. Please refer to the LICENSE file for details.

## 🙏 Acknowledgments

Built with excellent open-source tools:
- [Streamlit](https://streamlit.io/) - Web framework
- [LangChain](https://langchain.com/) - LLM framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenAI](https://openai.com/) - Language models
- [Unstructured](https://unstructured.io/) - Document processing

---

**IntelliDocs Pro** - Transform your documents into an intelligent knowledge base! 🚀