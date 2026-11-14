# HR Policy RAG Assistant

An interactive question-answering assistant for the Acme Corp demo employee handbook. The application uses retrieval-augmented generation (RAG) to find relevant sections of the HR policy before generating an answer, rather than asking the language model to answer from general knowledge.

The project provides:

- A Streamlit chat interface for interactive questions.
- A command-line demo with example HR questions.
- A reusable RAG pipeline split into small Python modules.
- A local FAISS vector index that is built once and reused on later runs.
- A bundled sample policy covering leave, remote work, probation, notice periods, reimbursements, conduct, holidays, and the exit process.

> **Important:** This repository contains a demo policy document. It is not a substitute for official HR guidance, an employment contract, or legal advice.

## How it works

The assistant follows this flow when it starts:

1. Load `data/hr_policy.txt`.
2. Split the policy into overlapping text chunks.
3. Generate Jina embeddings for the chunks.
4. Build and save a FAISS index in `data/faiss_index/`, or load the existing index if it is already present.
5. Create a retriever that returns the three most relevant chunks for a question.
6. Expose the retriever as the `search_hr_policy` LangChain tool.
7. Ask the Groq-hosted language model to use that tool before answering.

The system prompt instructs the assistant to say that it does not know when the answer is not present in the retrieved policy content.

## Architecture

```text
data/hr_policy.txt
        |
        v
document_loader.py -> splitter.py -> embeddings.py -> vector_store.py
                                                        |
                                                        v
                                                   FAISS index
                                                        |
                                                        v
question -> retriever -> search_hr_policy tool -> Groq LLM -> answer
                                                        |
                         +------------------------------+
                         |
              app.py (Streamlit) / main.py (CLI)
```

### Project structure

```text
.
├── app.py                    # Streamlit chat application
├── main.py                   # CLI demo with sample questions
├── requirements.txt          # Python dependencies
├── .env                      # Local API keys; do not commit
├── data/
│   ├── hr_policy.txt         # Source policy document
│   └── faiss_index/          # Persisted FAISS index and metadata
├── hr_assistant/
│   ├── agent.py              # Creates the LangChain agent
│   ├── config.py             # Environment variables and RAG settings
│   ├── document_loader.py    # Loads the policy text
│   ├── embeddings.py         # Configures Jina embeddings
│   ├── llm.py                # Configures the Groq chat model
│   ├── pipeline.py           # Builds the complete assistant
│   ├── splitter.py           # Splits documents into chunks
│   ├── tools.py              # Defines the policy search tool
│   └── vector_store.py       # Builds, saves, and loads FAISS
└── rag.ipynb                 # Notebook for experimenting with the RAG workflow
```

## Requirements

- Python 3.10 or newer
- A Groq API key
- A Jina AI API key
- Internet access when creating embeddings or querying the hosted LLM

The application depends on:

- [LangChain](https://www.langchain.com/) for the RAG and agent pipeline
- [Groq](https://groq.com/) through `langchain-groq` for chat completion
- [Jina AI](https://jina.ai/) through `JinaEmbeddings` for document embeddings
- [FAISS](https://faiss.ai/) for local vector search
- [Streamlit](https://streamlit.io/) for the web interface
- `python-dotenv` for loading local environment variables

## Installation on Windows

From the repository root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell prevents script activation, activate the environment from Command Prompt instead:

```bat
.venv\Scripts\activate.bat
```

## Configuration

Create a `.env` file in the repository root:

```dotenv
GROQ_API_KEY=your_groq_api_key
JINA_API_KEY=your_jina_api_key
```

Never commit API keys or copy them into source files. The `.env` file is ignored by Git. If a key has been exposed, revoke it and create a replacement.

The main runtime settings are in `hr_assistant/config.py`:

| Setting | Default | Purpose |
| --- | --- | --- |
| `DATA_FILE_PATH` | `data/hr_policy.txt` | Source policy document |
| `VECTOR_STORE_PATH` | `data/faiss_index` | Persisted FAISS index directory |
| `LLM_MODEL_NAME` | `openai/gpt-oss-20b` | Groq model name |
| `EMBEDDING_MODEL_NAME` | `jina-embeddings-v2-base-en` | Jina embedding model |
| `CHUNK_SIZE` | `500` | Maximum chunk size |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K_RESULTS` | `3` | Number of chunks retrieved per question |

## Run the application

### Streamlit chat interface

```powershell
streamlit run app.py
```

Streamlit opens the assistant in a browser. Ask questions such as:

- How many paid annual leave days are available?
- How many days of remote work are allowed each week?
- What is the notice period during probation?
- How long do reimbursement claims take to process?

### Command-line demo

```powershell
python main.py
```

The CLI builds the assistant and runs three sample questions.

## Updating the policy document

1. Replace or edit `data/hr_policy.txt`.
2. Remove the existing persisted index files from `data/faiss_index/`:

   ```powershell
   Remove-Item data\faiss_index\index.faiss, data\faiss_index\index.pkl
   ```

3. Start the application again.

The pipeline detects that the index is missing, re-embeds the updated document, and saves a new index. The first build may take longer because it calls the Jina embedding service.

## Troubleshooting

### Missing API key

The application validates both keys at startup. Confirm that `.env` is in the repository root and contains non-empty `GROQ_API_KEY` and `JINA_API_KEY` values.

### The application still answers from an old policy

Delete the files in `data/faiss_index/` and restart the application so the policy is embedded again.

### FAISS deserialization warning

The application loads the local FAISS metadata with `allow_dangerous_deserialization=True` because the index is created and stored by this project. Only load index files from a trusted source.

## Limitations

- The assistant can only answer questions supported by the contents of `data/hr_policy.txt`.
- Answers depend on the quality of retrieval and the configured model.
- API access to Groq and Jina is required for a fresh setup or index rebuild.
- The persisted FAISS index must be rebuilt manually after changing the source policy.
- There is no authentication, authorization, database-backed conversation storage, or production deployment configuration.
- The Streamlit conversation history exists only for the current browser session.

## Development notes

The shared entry point is `build_hr_assistant()` in `hr_assistant/pipeline.py`. Both `app.py` and `main.py` use this function, so changes to document loading, retrieval, model configuration, or agent behavior should normally be made in the `hr_assistant/` package rather than duplicated in the entry points.

The notebook `rag.ipynb` is available for step-by-step experimentation, while the Python modules provide the reusable application implementation.
