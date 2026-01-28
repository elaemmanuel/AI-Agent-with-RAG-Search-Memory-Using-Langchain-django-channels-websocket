# AI Conversational Agent with RAG Memory

**Recruiter Hook:**  
MSc Computer Science student building real-time AI applications using Django, LangChain, WebSockets, and Retrieval-Augmented Generation (RAG). Live demo available at https://agentel-app.onrender.com

## Overview
This project is a real-time AI conversational agent that maintains persistent chat memory and supports **Retrieval-Augmented Generation (RAG)** for grounded, context-aware responses.
The system uses Django Channels and WebSockets for asynchronous communication, LangChain for agent orchestration, and PostgreSQL for durable conversation history.

The architecture is designed to support dynamic document ingestion and retrieval, with a production-ready RAG pipeline implemented in the backend.

## Features
- **Retrieval-Augmented Generation (RAG):** Documents are embedded and stored in a FAISS vector store, allowing relevant context to be retrieved and injected into the LLM prompt before response generation.
- **Persistent Chat Memory:** Conversation history is stored in PostgreSQL and reloaded per session, enabling continuity across messages and reconnections.
- **Real-Time Communication (WebSockets):** Django Channels enables low-latency, bidirectional communication for a responsive chat experience.
- **Async & Scalable Backend:** HNon-blocking LLM calls and background-safe execution using async consumers and thread pools.
- **Live Hosted Demo:** Deployed on Render with PostgreSQL-backed memory persistence.

## Tech Stack
- **Backend:** Python, Django, Django REST Framework, Django Channels, Async
- **Frontend:** JavaScript, WebSockets
- **Database:** PostgreSQL (hosted on Render)
- **AI & Automation:** LangChain, FAISS, HuggingFace Embeddings, RAG

## Architecture Review
- User sends a message via WebSocket.
- Django Channels consumer receives the message asynchronously.
- LangChain agent evaluates whether to:
    - respond directly,
    - retrieve context from documents (RAG),
    - or use external search tools.
- Retrieved context (if any) is injected into the LLM prompt.
- The generated response is sent back to the client in real time.
- Conversation history is persisted in PostgreSQL.

## How to Run Locally
1. Clone the repository:
```bash
git clone https://github.com/elaemmanuel/AI-Agent-with-RAG-Search-Memory-Using-Langchain-django-channels-websocket.git
```

2. Navigate inot project's directory

3. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

5. Install dependencies
```bash
pip install -r requirements.txt
```

6. Configure environmental variables

7. Apply migration and start server
```bash
python manage.py migrate
python manage.py runserver
```

## Usage Example
- Open the web interface or connect via WebSockets.
- Ask a question, and the AI agent will answer using RAG to provide context-aware responses.
- Previous conversations are remembered and influence the AI’s answers.

## Demo
- Live demo hosted at: https://agentel-app.onrender.com

## Deployment Notes (Important)
The backend includes functionality for uploading documents and dynamically rebuilding the FAISS vector store for RAG.
However, **document upload is disabled in the live demo** due to hosting constraints on the free deployment tier. The RAG pipeline itself is fully implemented and functional when run locally or on a production-tier environment.

## Future Improvements
- Enable multi-user authentication and isolated memory per user.
- Add streaming responses for improved UX.
- Extend document ingestion to support multiple file formats.
- Introduce monitoring and analytics for conversation patterns.
- Deploy on a production-tier environment with dynamic document ingestion enabled.


