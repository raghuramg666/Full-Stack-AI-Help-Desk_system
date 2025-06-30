![image](https://github.com/user-attachments/assets/3767d050-affa-44b6-89ba-ff0c509975e3)
![image](https://github.com/user-attachments/assets/9d10cf6c-1964-4205-92f2-1cf1f8b8165a)
![image](https://github.com/user-attachments/assets/ea335cdd-0b06-48fc-abaf-c70ae8a9f4f1)

![image](https://github.com/user-attachments/assets/329ef6b1-8a8c-4d0c-a1e5-b84648677caf)

![image](https://github.com/user-attachments/assets/587f8689-7100-4ea8-bb73-51784a13154b)



## IT Helpdesk Chatbot – AI-Powered Support Assistant

This project is an intelligent, interactive IT Helpdesk Chatbot built using FastAPI, OpenAI GPT, and HTML/JavaScript frontend, designed to streamline IT support workflows in organizations. It delivers instant, professional assistance for common IT issues such as password resets, software installation, hardware failures, and network problems.

> Deployment: This chatbot is also deployed using Streamlit Cloud, allowing live demo access with a simplified interface built via `main_streamlit.py`.

---

### Key Features

* Conversational AI Assistance
  Uses OpenAI GPT to generate clear, professional, human-like responses based on company documentation and user intent.

* Multi-Step Onboarding
  Guides the user through name, contact, and issue category collection before starting the chat.

* Smart Query Classification
  Automatically identifies the type of query (e.g., password reset, hardware failure, network issue) using rules or ML logic.

* Critical Issue Detection and Escalation
  Detects urgency indicators like "important", "emergency", "urgent" and visually escalates with a red status bubble beside the chat.

* Context-Aware Responses
  Retrieves relevant documentation chunks based on query category for grounding the AI’s reply.

* Conversation Memory
  Maintains a running history of the session per user, saved in JSON format for continuity and tracking.

* Feedback Collection and Session Management
  After resolution, users can submit optional feedback or start a new session with a single click.

* Robust Logging System
  Every request, response, and error across modules is logged via Python’s `logging` module, stored in a `logs/` directory.

---

### Tech Stack

* Backend: FastAPI, Pydantic, Python AsyncIO
* Frontend: HTML, JavaScript, CSS
* LLM: OpenAI GPT-3.5 (via `openai` Python SDK)
* Data Source: Markdown/JSON document chunks
* Logging: Python logging with rotating file handler
* Session Storage: JSON file-based user history
* Deployment:

  * FastAPI version for traditional hosting (Fly.io, Render, etc.)
  * Streamlit version powered by `main_streamlit.py` for easy Streamlit Cloud deployment and live demos

---

### Use Cases

* Internal IT support portal
* LLM-powered employee helpdesk assistant
* AI chatbot demo for educational or enterprise prototypes
* GenAI-based support automation showcase

---

### Project Structure

* `main.py` – FastAPI entry point for backend APIs
* `main_streamlit.py` – Streamlit interface for quick online deployment
* `respond.py` – Generates OpenAI GPT responses
* `classify.py` – Request categorization logic
* `escalate.py` – Detects urgent/escalation-worthy issues
* `retrieve.py` – Context chunk retriever based on category
* `logs/` – Logging and chat history
* `static/` – JavaScript and CSS
* `templates/` – HTML-based frontend
* `documents/` – Knowledge base snippets
* `test_cases/` – Contains structured test scenarios



### Planned Improvements

* Add vector database support (FAISS/Weaviate) for enhanced retrieval
* Admin dashboard to monitor escalations and user feedback
* User authentication with role-based permissions
* Containerize with Docker for scalable deployment
* Multilingual and voice support for broader accessibility
