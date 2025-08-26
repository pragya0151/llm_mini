# backend/server.py
from fastapi import FastAPI, UploadFile, File, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
from typing import List, Optional, Dict
from urllib.parse import quote_plus

from langchain_community.llms import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Your existing PDF processing modules
from .ingest import load_and_chunk
from .embeddings import build_vector_db
from .retriever import get_qa_chain
from .highlight_pdf import highlight_pdf

# --------------------------
# App setup
# --------------------------
app = FastAPI(title="Professional RAG Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --------------------------
# Global state
# --------------------------
_state = {
    "files": [],       # local paths of uploaded PDFs
    "vector_db": None,
    "qa_chain": None,
}

llm = Ollama(model="tinyllama")  # Tiny LLaMA instance 

# --------------------------
# Helpers
# --------------------------
def _normalize_chain_result(result) -> Dict:
    """
    Convert various possible chain return types into a dict with:
      - 'answer' (str)
      - 'source_documents' (list)
    """
    if isinstance(result, dict):
        #  handle common LangChain formats
        if "text" in result:  # from LLMChain
            return {"answer": result["text"], "source_documents": []}
        if "answer" in result or "result" in result:
            return {
                "answer": result.get("answer") or result.get("result"),
                "source_documents": result.get("source_documents", [])
            }
        # fallback
        return {"answer": str(result), "source_documents": []}

    if isinstance(result, str):
        return {"answer": result, "source_documents": []}

    # fallback for weird objects
    return {"answer": str(result), "source_documents": []}


# --------------------------
# Upload PDFs
# --------------------------
@app.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    # clear previous files (for demo simplicity)
    _state["files"].clear()
    all_chunks = []

    for f in files:
        safe_name = f.filename.replace("/", "_").replace("..", "_")
        path = os.path.join(UPLOAD_FOLDER, safe_name)
        with open(path, "wb") as out:
            out.write(await f.read())
        _state["files"].append(path)
        chunks = load_and_chunk(path)
        all_chunks.extend(chunks)

    # Build vector DB and QA chain
    vector_db = build_vector_db(all_chunks)
    _state["vector_db"] = vector_db
    _state["qa_chain"] = get_qa_chain(vector_db)

    return JSONResponse({
        "status": "ok",
        "files": [os.path.basename(p) for p in _state["files"]]
    })


# --------------------------
# Ask a query
# --------------------------
@app.get("/ask")
async def ask(request: Request, query: str = Query(...), eli5: Optional[bool] = False):
    # generic greetings that deserve a canned reply if no docs are present
    greetings = {"hello", "hi", "how are you", "thanks", "thank you", "hey"}
    prompt_text = query
    if eli5:
        prompt_text = f"Explain like I'm 5: {prompt_text}"

    if query.strip().lower() in greetings and not _state["qa_chain"]:
        return JSONResponse({"answer": "Hello! How can I assist you today?", "sources": [], "highlighted_pdfs": []})

    answer = ""
    sources_text = []
    highlighted_pdfs = []

    try:
        if _state["qa_chain"]:
            # PDF-augmented QA
            raw = _state["qa_chain"].invoke({"query": prompt_text})
            res = _normalize_chain_result(raw)

            answer = res.get("answer", "")
            source_docs = res.get("source_documents", []) or []

            # Build sources text (short snippets) for frontend and also group by source PDF
            grouped_by_source: Dict[str, List[str]] = {}
            for i, doc in enumerate(source_docs):
                # doc may be LangChain Document; try to fetch page_content and metadata.source
                content = getattr(doc, "page_content", None) or getattr(doc, "content", None) or str(doc)
                metadata = getattr(doc, "metadata", {}) or {}
                src = metadata.get("source") or metadata.get("file") or metadata.get("filename") or None

                # add to sources_text (short snippet)
                snippet = (content[:700] + "...") if content and len(content) > 700 else (content or "")
                sources_text.append({"text": snippet, "confidence_rank": i + 1})

                if src:
                    grouped_by_source.setdefault(src, []).append(content)

            # For each source file that exists locally, create a highlighted PDF and collect chunks
            for src_path, contents in grouped_by_source.items():
                candidate = src_path
                if not os.path.isabs(candidate):
                    base = os.path.basename(candidate)
                    matches = [p for p in _state["files"] if os.path.basename(p) == base]
                    candidate = matches[0] if matches else candidate

                if not os.path.exists(candidate):
                    continue

                all_matched_snippets = []
                for idx_doc, content in enumerate(contents[:8]):
                    out_path = candidate + f".highlighted.{idx_doc}.pdf"
                    try:
                        matched = highlight_pdf(candidate, content, out_path)  # returns list[str]
                        if matched:
                            all_matched_snippets.extend(matched)
                    except Exception as e:
                        print(f"Highlight failed for {candidate}: {e}")

                if all_matched_snippets:
                    deduped = []
                    for s in all_matched_snippets:
                        if s not in deduped:
                            deduped.append(s)
                    download_path = os.path.abspath(out_path)
                    download_url = f"/download?path={quote_plus(download_path)}"
                    highlighted_pdfs.append({
                        "name": os.path.basename(candidate),
                        "chunks": deduped,
                        "download_path": download_path,
                        "download_url": download_url
                    })

        else:
            # No PDFs uploaded — fallback to plain LLM
            prompt = PromptTemplate(input_variables=["query"], template="{query}")
            chain = LLMChain(llm=llm, prompt=prompt)
            raw = chain.invoke({"query": prompt_text})
            res = _normalize_chain_result(raw)
            answer = res.get("answer", "")

    except Exception as exc:
        answer = f"Backend error: {exc}"

    return JSONResponse({
        "answer": answer,
        "sources": sources_text,
        "highlighted_pdfs": highlighted_pdfs
    })


# --------------------------
# Clear uploaded files / reset
# --------------------------
@app.post("/clear_uploads")
async def clear_uploads():
    _state["files"].clear()
    _state["vector_db"] = None
    _state["qa_chain"] = None
    return JSONResponse({"status": "uploads cleared"})


# --------------------------
# Download highlighted PDF
# --------------------------
@app.get("/download")
async def download(path: str):
    norm = os.path.abspath(path)
    if not norm.startswith(os.path.abspath(BASE_DIR)):
        return JSONResponse({"error": "Invalid path"}, status_code=400)
    if not os.path.exists(norm):
        return JSONResponse({"error": "File not found"}, status_code=404)
    return FileResponse(norm, filename=os.path.basename(norm))

