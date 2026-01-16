# AI Conversational Agent with RAG Memory

**Recruiter Hook:**  
MSc Computer Science student building real-time AI applications with Django, LangChain, and RAG. Live demo available at [agentel-app.onrender.com](https://agentel-app.onrender.com).

## Overview
This project is an AI conversational agent that remembers past interactions and uses **Retrieval-Augmented Generation (RAG)** to answer questions with context from previous chats. It provides a real-time chat interface and leverages LangChain for intelligent RAG-based responses. The backend is built with Django and Django Channels, supporting async communication and scalable memory storage.

## Features
- **RAG Search with LangChain:** Retrieves relevant information to provide context-aware answers.
- **Persistent Chat Memory:** Stores past conversations for continuity in interactions.
- **Real-time UI via WebSockets:** Enables instant communication between the frontend and backend.
- **Django Backend with Async Support:** Handles real-time requests efficiently and integrates with a PostgreSQL database.
- **Hosted Demo:** Available live at [AI Agent Demo](https://agentel-app.onrender.com).

## Tech Stack
- **Backend:** Python, Django, Django REST Framework, Django Channels, Async
- **Frontend:** JavaScript, WebSockets
- **Database:** PostgreSQL (hosted on Render)
- **AI & Automation:** LangChain, RAG

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

## Future Improvements
- Improve frontend UI for a better user experience.
- Add user authentication to separate multiple users’ memory.
- Extend AI capabilities with additional LLMs and datasets.
- Add analytics to track conversation patterns.



