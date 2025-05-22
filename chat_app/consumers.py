
# import json
# import os
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from channels.generic.websocket import AsyncWebsocketConsumer
# from langchain.agents import AgentType, initialize_agent
# from langchain_community.utilities import SerpAPIWrapper
# from langchain_community.vectorstores import FAISS
# from langchain_core.prompts import PromptTemplate
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain.tools import Tool
# from langchain_core.tools import tool
# from langchain_groq import ChatGroq
# from django.conf import settings
# from .memory import DjangoChatMessageHistory
# from langchain_community.document_loaders import PyPDFLoader
# import traceback
# from asgiref.sync import async_to_sync

# class ChatConsumer(AsyncWebsocketConsumer):
#     _llm = None
#     _vector_store = None
#     _retrieval_tool = None
#     _search_tool = None
#     _initialized_globals = False

#     persistent_memory = None
#     agent = None
#     prompt = None
#     room_name = "AgenteL"
#     room_group_name = f'chat_{room_name}'

#     @classmethod
#     async def _global_initialize(cls):
#         if cls._initialized_globals:
#             print("Global components already initialized. Skipping.")
#             return

#         print("--- Globally initializing LangChain resources (once per app startup) ---")

#         print("  - Initializing ChatGroq LLM...")
#         cls._llm = ChatGroq(temperature=0.4, model_name="llama-3.3-70b-versatile")
#         print("  - ChatGroq LLM initialized.")

#         print("  - Initializing HuggingFaceEmbeddings and FAISS Vector Store...")
#         embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
#         pdf_path = os.path.join(settings.BASE_DIR, 'data', 'bitcoin.pdf')
#         all_splits = []

#         loop = asyncio.get_event_loop()
#         with ThreadPoolExecutor() as pool:
#             try:
#                 loader = PyPDFLoader(pdf_path)
#                 docs = await loop.run_in_executor(pool, loader.load)
#                 text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#                 all_splits = await loop.run_in_executor(pool, text_splitter.split_documents, docs)

#                 cls._vector_store = await FAISS.afrom_documents(all_splits, embeddings)
#                 print("  - FAISS Vector Store created successfully.")

#                 @tool
#                 async def retrieve_docs_async(query: str) -> str:
#                     """
#                     Use this tool to find and retrieve specific information from the loaded document.
#                     Input: A precise question or keyword to search within the document (e.g., "What is Bitcoin?", "define electronic cash").
#                     Output: The most relevant text passages from the document directly answering the input query.
#                     """
#                     print(f"DEBUG: retrieve_docs_async called with query: '{query}'")
#                     if cls._vector_store:
#                         retrieved_docs = await cls._vector_store.asimilarity_search(query, k=1)
#                         print(f"DEBUG: Retrieved docs count: {len(retrieved_docs)}")
#                         if not retrieved_docs:
#                             print("DEBUG: No relevant information found in the document for that query.")
#                             return "No relevant information found in the document for that query."

#                         # Add clear markers to the output
#                         serialized = "--- Document Content Start ---\n"
#                         serialized += "\n\n".join(
#                             (f"Source: {doc.metadata.get('source', 'Unknown')}\n" f"Content: {doc.page_content}")
#                             for doc in retrieved_docs
#                         )
#                         serialized += "\n--- Document Content End ---"

#                         print(f"DEBUG: Serialized retrieved content (first 500 chars):\n{serialized[:500]}...")
#                         return serialized
#                     print("DEBUG: Vector store not initialized in retrieve_docs_async.")
#                     return "No documents loaded for retrieval."

#                 cls._retrieval_tool = retrieve_docs_async
#                 print("  - Document Retrieval tool created.")
#             except FileNotFoundError:
#                 print(f"Error: PDF file not found at {pdf_path}. Document retrieval will be unavailable.")
#                 cls._retrieval_tool = Tool(
#                     name="Document Retrieval",
#                     func=lambda q: "Error: Document retrieval not available (PDF not found).",
#                     description="useful for when you need to answer questions based on the provided documents.",
#                 )
#             except Exception as e:
#                 print(f"Error during RAG initialization (PDF/FAISS): {e}")
#                 cls._retrieval_tool = Tool(
#                     name="Document Retrieval",
#                     func=lambda q: f"Error: Document retrieval encountered an issue: {e}",
#                     description="useful for when you need to answer questions based on the provided documents.",
#                 )

#         print("  - Initializing SerpAPI Search Tool...")
#         cls._search_tool = Tool(
#             name="Search",
#             func=SerpAPIWrapper().run,
#             description="useful for when you need to answer questions about current events or general knowledge. Be concise in your search queries.",
#         )
#         print("  - SerpAPI Search Tool initialized.")

#         cls._initialized_globals = True
#         print("--- Global LangChain resources initialization complete ---")


#     async def connect(self):
#         self.room_name = "AgenteL"
#         self.room_group_name = f'chat_{self.room_name}'
#         self.session_id = self.channel_name

#         self.persistent_memory = DjangoChatMessageHistory(session_id=self.session_id)

#         tools = [self.__class__._search_tool, self.__class__._retrieval_tool]
#         self.prompt = PromptTemplate.from_template(
#             """You are AgenteL, a helpful, concise, and direct AI assistant. You can have conversations and use tools to provide information. When a user introduces themselves or engages in general conversation, respond appropriately without trying to use a tool unless a clear question or need for information arises.

#             You have access to the following tools:

#             1.  **Document Retrieval**: Use this tool ONLY when the user's question asks for information specifically from the provided documents (e.g., "in this document", "according to the paper", or direct questions about Bitcoin's definition from the loaded document).
#                 - **Tool Input**: A direct, concise question or keyword to search within the document (e.g., "definition of Bitcoin", "peer-to-peer electronic cash system").
#                 - **Tool Output**: Raw text content retrieved from the document.
#                 - **Crucial Action**: Once the Document Retrieval tool returns its output, **immediately use the information within that output to directly answer the user's question.** Do NOT re-ask for the document. Do NOT generate new actions unless absolutely necessary to formulate a final answer based *solely* on the retrieved content. If the tool output is empty or says "No relevant information found", clearly state that.

#             2.  **Search**: Use this tool for general knowledge, current events, or information not expected to be in the provided documents.
#                 - **Tool Input**: A concise search query (e.g., "current price of Bitcoin", "news about AI").
#                 - **Tool Output**: Search results from the web.
#                 - **Crucial Action**: Use the search results to answer the question.

#             Current conversation:
#             {history}
#             User: {input}
#             AI:"""
#         )
#         self.agent = initialize_agent(
#             tools,
#             self.__class__._llm,
#             agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION, # <--- CHANGED AGENT TYPE BACK TO CONVERSATIONAL
#             memory=self.persistent_memory,
#             verbose=True,
#             handle_parsing_errors="Check your output and try again.",
#         )

#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()
#         print(f"WebSocket connected for session: {self.session_id}")


#     async def disconnect(self, close_code):
#         print(f"WebSocket disconnected for session: {self.session_id} with code: {close_code}")
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']

#         if not self.agent:
#             await self.send(text_data=json.dumps({'message': "Error: Agent not initialized for this session. Please refresh."}))
#             return

#         response_content = "An error occurred."
#         try:
#             loaded_memory_dict = await self.persistent_memory.aload_memory_variables({})
#             agent_inputs = {
#                 "input": message,
#                 "chat_history": loaded_memory_dict.get("history", [])
#             }
#             response = await self.agent.ainvoke(agent_inputs)
#             response_content = response.get("output", "No response output from agent.")

#         except Exception as e:
#             print(f"Error during agent processing for session {self.session_id}: {e}")
#             response_content = "Sorry, there was an error processing your request. Please try again later."
#             traceback.print_exc()

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat.message',
#                 'message': response_content,
#             }
#         )

#     async def chat_message(self, event):
#         message = event['message']
#         await self.send(text_data=json.dumps({
#             'message': message
#         }))



# chat_app/consumers.py

import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from channels.generic.websocket import AsyncWebsocketConsumer
from langchain.agents import AgentType, initialize_agent
from langchain_community.utilities import SerpAPIWrapper
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools import Tool
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from django.conf import settings
from .memory import DjangoChatMessageHistory
from langchain_community.document_loaders import PyPDFLoader
import traceback
from asgiref.sync import sync_to_async # Import sync_to_async for view integration

class ChatConsumer(AsyncWebsocketConsumer):
    _llm = None
    _vector_store = None # This will now store the *current* FAISS instance
    _retrieval_tool = None
    _search_tool = None
    _initialized_globals = False
    _document_paths = [] # Class-level list to keep track of all loaded document paths

    persistent_memory = None
    agent = None
    prompt = None
    room_name = "AgenteL"
    room_group_name = f'chat_{room_name}'

    @classmethod
    async def _load_documents_into_vector_store(cls, document_paths: list[str]):
        """
        Loads documents from specified paths, splits them, and creates/rebuilds the FAISS vector store.
        """
        print(f"  - Loading documents from paths: {document_paths}")
        all_splits = []
        loop = asyncio.get_event_loop()
        
        # Use a ThreadPoolExecutor for blocking I/O (like PDF loading)
        with ThreadPoolExecutor() as pool:
            for doc_path in document_paths:
                if not os.path.exists(doc_path):
                    print(f"  - Warning: Document not found at {doc_path}. Skipping.")
                    continue
                try:
                    loader = PyPDFLoader(doc_path)
                    docs = await loop.run_in_executor(pool, loader.load)
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    splits = await loop.run_in_executor(pool, text_splitter.split_documents, docs)
                    all_splits.extend(splits)
                    print(f"  - Loaded and split {len(docs)} pages from {os.path.basename(doc_path)}")
                except Exception as e:
                    print(f"  - Error loading {doc_path}: {e}")

        if all_splits:
            print(f"  - Creating/Rebuilding FAISS Vector Store with {len(all_splits)} chunks...")
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
            cls._vector_store = await FAISS.afrom_documents(all_splits, embeddings)
            print("  - FAISS Vector Store created successfully.")
            cls._document_paths = list(set(document_paths)) # Update the class-level list of paths
        else:
            print("  - No documents found or loaded. FAISS Vector Store will be empty.")
            cls._vector_store = None # Ensure it's None if no docs are loaded

    @classmethod
    async def _global_initialize(cls):
        if cls._initialized_globals:
            print("Global components already initialized. Skipping.")
            return

        print("--- Globally initializing LangChain resources (once per app startup) ---")

        print("  - Initializing ChatGroq LLM...")
        cls._llm = ChatGroq(temperature=0.4, model_name="llama-3.3-70b-versatile")
        print("  - ChatGroq LLM initialized.")

        # Define initial document path(s)
        initial_doc_paths = []
        bitcoin_pdf_path = os.path.join(settings.BASE_DIR, 'data', 'bitcoin.pdf')
        if os.path.exists(bitcoin_pdf_path):
            initial_doc_paths.append(bitcoin_pdf_path)

        # Load initial documents into the vector store
        await cls._load_documents_into_vector_store(initial_doc_paths)

        @tool
        async def retrieve_docs_async(query: str) -> str:
            """
            Use this tool to find and retrieve specific information from the loaded document(s).
            Input: A precise question or keyword to search within the document (e.g., "What is Bitcoin?", "define electronic cash").
            Output: The most relevant text passages from the document directly answering the input query.
            """
            print(f"DEBUG: retrieve_docs_async called with query: '{query}'")
            if cls._vector_store:
                retrieved_docs = await cls._vector_store.asimilarity_search(query, k=1)
                print(f"DEBUG: Retrieved docs count: {len(retrieved_docs)}")
                if not retrieved_docs:
                    print("DEBUG: No relevant information found in the document(s) for that query.")
                    return "No relevant information found in the document(s) for that query."

                serialized = "--- Document Content Start ---\n"
                serialized += "\n\n".join(
                    (f"Source: {doc.metadata.get('source', 'Unknown')}\n" f"Content: {doc.page_content}")
                    for doc in retrieved_docs
                )
                serialized += "\n--- Document Content End ---"

                print(f"DEBUG: Serialized retrieved content (first 500 chars):\n{serialized[:500]}...")
                return serialized
            print("DEBUG: Vector store not initialized in retrieve_docs_async.")
            return "No documents loaded for retrieval."

        cls._retrieval_tool = retrieve_docs_async
        print("  - Document Retrieval tool created.")

        print("  - Initializing SerpAPI Search Tool...")
        cls._search_tool = Tool(
            name="Search",
            func=SerpAPIWrapper().run,
            description="useful for when you need to answer questions about current events or general knowledge. Be concise in your search queries.",
        )
        print("  - SerpAPI Search Tool initialized.")

        cls._initialized_globals = True
        print("--- Global LangChain resources initialization complete ---")

    @classmethod
    async def trigger_rag_update_with_new_file(cls, new_file_path: str):
        """
        Triggers a rebuild of the RAG vector store to include a new file.
        This method is designed to be called from a Django view (via sync_to_async).
        """
        print(f"RAG Update Triggered: Adding {new_file_path}")
        
        # Add the new file path to the list of documents to load
        current_document_paths = list(cls._document_paths) # Make a copy
        if new_file_path not in current_document_paths:
            current_document_paths.append(new_file_path)
            
        await cls._load_documents_into_vector_store(current_document_paths)
        print(f"RAG Update Complete: Vector store rebuilt with {len(current_document_paths)} documents.")


    async def connect(self):
        self.room_name = "AgenteL"
        self.room_group_name = f'chat_{self.room_name}'
        self.session_id = self.channel_name

        self.persistent_memory = DjangoChatMessageHistory(session_id=self.session_id)

        tools = [self.__class__._search_tool, self.__class__._retrieval_tool]
        self.prompt = PromptTemplate.from_template(
            """You are AgenteL, a helpful, concise, and direct AI assistant. You can have conversations and use tools to provide information. When a user introduces themselves or engages in general conversation, respond appropriately without trying to use a tool unless a clear question or need for information arises.

            You have access to the following tools:

            1.  **Document Retrieval**: Use this tool ONLY when the user's question asks for information specifically from the loaded document(s) (e.g., "in this document", "according to the paper", or direct questions about X from the loaded document).
                - **Tool Input**: A direct, concise question or keyword to search within the document (e.g., "definition of Bitcoin", "peer-to-peer electronic cash system").
                - **Tool Output**: Raw text content retrieved from the document.
                - **Crucial Action**: Once the Document Retrieval tool returns its output, **immediately use the information within that output to directly answer the user's question.** Do NOT re-ask for the document. Do NOT generate new actions unless absolutely necessary to formulate a final answer based *solely* on the retrieved content. If the tool output is empty or says "No relevant information found", clearly state that.

            2.  **Search**: Use this tool for general knowledge, current events, or information not expected to be in the provided documents.
                - **Tool Input**: A concise search query (e.g., "current price of Bitcoin", "news about AI").
                - **Tool Output**: Search results from the web.
                - **Crucial Action**: Use the search results to answer the question.

            Current conversation:
            {history}
            User: {input}
            AI:"""
        )
        self.agent = initialize_agent(
            tools,
            self.__class__._llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.persistent_memory,
            verbose=True,
            handle_parsing_errors="Check your output and try again.",
        )

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"WebSocket connected for session: {self.session_id}")


    async def disconnect(self, close_code):
        print(f"WebSocket disconnected for session: {self.session_id} with code: {close_code}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        if not self.agent:
            await self.send(text_data=json.dumps({'message': "Error: Agent not initialized for this session. Please refresh."}))
            return

        response_content = "An error occurred."
        try:
            loaded_memory_dict = await self.persistent_memory.aload_memory_variables({})
            agent_inputs = {
                "input": message,
                "chat_history": loaded_memory_dict.get("history", [])
            }
            response = await self.agent.ainvoke(agent_inputs)
            response_content = response.get("output", "No response output from agent.")

        except Exception as e:
            print(f"Error during agent processing for session {self.session_id}: {e}")
            response_content = "Sorry, there was an error processing your request. Please try again later."
            traceback.print_exc()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': response_content,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))