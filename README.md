## MINI LLM

<img width="1916" height="902" alt="image" src="https://github.com/user-attachments/assets/cf05bda2-07a4-46b5-9965-9b048e78fed6" />




Professional RAG Chat is a web application that allows users to ask questions on uploaded PDFs using a lightweight Tiny LLaMA model combined with a FAISS vector database for fast retrieval. It can also answer general knowledge queries even without uploaded files and highlights relevant sections in PDFs for easy reference.

---

## How It Works

1. **PDF Upload & Processing**  
   Users can upload one or more PDFs. Each PDF is automatically chunked into smaller segments, indexed, and stored in a FAISS vector database for efficient retrieval.
   
   <img width="1829" height="684" alt="image" src="https://github.com/user-attachments/assets/46a93904-ae8c-4d0b-ae71-64f1f9d13e43" />

3. **RAG (Retrieval-Augmented Generation)**  
   Questions are processed using a Tiny LLaMA model combined with the FAISS database. The system retrieves relevant chunks from PDFs and generates context-aware answers.
   
   <img width="1771" height="708" alt="Screenshot 2025-08-26 113959" src="https://github.com/user-attachments/assets/aaad0aa5-8d79-4b0b-bcf0-9a97bc839f34" />

4. **General Knowledge Queries**  
   If no PDFs are uploaded, the Tiny LLaMA model alone answers questions using its internal knowledge.
   
   <img width="1708" height="756" alt="Screenshot 2025-08-26 124858" src="https://github.com/user-attachments/assets/5e3e8e79-f5b6-4b2a-9384-2edf000e3232" />

5. **Highlighting Sources**  
   Relevant snippets from uploaded PDFs are highlighted and displayed along with the answer.
   
   <img width="1739" height="711" alt="Screenshot 2025-08-26 114210" src="https://github.com/user-attachments/assets/a4546d7a-0690-4df5-bf4e-b37d5bce8cba" />

6. **Explain Like I’m 5**  
   Optional mode simplifies answers for easier understanding.

7. **FAQ Sidebar**  
   A dedicated sidebar contains frequently asked questions about RAG, uploading PDFs, Tiny LLaMA functionality, and general AI usage tips.
   
   <img width="570" height="831" alt="image" src="https://github.com/user-attachments/assets/b53208c9-6960-4ea3-9027-38685b8d867b" />
   
8. **Past Questions Section**  
   All previous user questions and their corresponding answers are stored in an expandable format, allowing users to quickly review past interactions. A “Clear History” button resets the chat session.
   
<img width="850" height="877" alt="image" src="https://github.com/user-attachments/assets/0dc85ffc-11d7-46dc-86f9-73f9a40a2c0a" />


9. **About me section to give users idea about this app**
<img width="724" height="465" alt="image" src="https://github.com/user-attachments/assets/e035059f-3fbf-4f3e-be6d-5be2f85d3c97" />

## workflow
<img width="626" height="659" alt="image" src="https://github.com/user-attachments/assets/93281a20-7228-4509-9f0f-8a55de471c08" />

## What We Are Coding

This project combines **frontend UI**, **backend API**, and **AI processing** to create an interactive question-answering system:

1. **Frontend (Streamlit)**  
   - Input box for user queries and "Explain Like I’m 5" checkbox.  
   - PDF upload section with "Process Files" button.  
   - Displays answers in a styled card format and shows highlighted PDF chunks.  
   - Sidebar contains FAQ and past question history.  

2. **Backend (FastAPI)**  
   - Accepts uploaded PDFs and stores them in a local folder.  
   - Chunks PDFs into smaller text segments for efficient retrieval.  
   - Builds a FAISS vector database to enable fast semantic search.  
   - Handles user queries:  
     - **With PDFs:** Queries the FAISS vector database to find relevant chunks and uses Tiny LLaMA to generate context-aware answers.  
     - **Without PDFs:** Uses only Tiny LLaMA to answer general questions.  
   - Generates highlighted PDF snippets for the frontend display.  
   - Provides endpoints for uploading files, querying answers, clearing uploads, and downloading highlighted PDFs.

3. **RAG (Retrieval-Augmented Generation) Logic**  
   - Uses FAISS to retrieve semantically relevant chunks from PDFs.  
   - Feeds retrieved chunks into the Tiny LLaMA model for coherent answer generation.  
   - Optional “Explain Like I’m 5” mode simplifies the output.  

4. **State Management**  
   - Keeps track of past user queries and assistant answers in Streamlit’s session state.  
   - Sidebar shows expandable past questions with corresponding answers for easy review.  

---

---

## Project structure
<img width="771" height="699" alt="image" src="https://github.com/user-attachments/assets/585eda6b-a7b3-4556-85e0-4fc5075adf27" />
