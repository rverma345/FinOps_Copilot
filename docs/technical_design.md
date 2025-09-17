# AI Cost & Insights Copilot - Technical Design Document

## 1. Architecture

The application is built using a microservices-like architecture. A **FastAPI** backend serves as the core API, which handles data retrieval, KPI calculations, and the RAG pipeline. A **Streamlit** UI provides a simple, interactive frontend for the user. The application's data is stored in a **SQLite** database for persistence and a **ChromaDB** vector store for the RAG pipeline.


## 2. Data Model

The data model is designed to be simple and extensible.
* **`billing` table**: Stores cloud usage and cost data.
    -   `invoice_month` (TEXT): The month and year of the invoice (e.g., '2023-05').
    -   `account_id` (TEXT): The cloud account identifier.
    -   `service` (TEXT): The cloud service (e.g., 'Amazon EC2').
    -   `resource_group` (TEXT): A logical group for resources.
    -   `resource_id` (TEXT): A unique identifier for the resource.
    -   `usage_qty` (REAL): The amount of resource usage.
    -   `unit_cost` (REAL): The cost per unit of usage.
    -   `cost` (REAL): The total cost for the resource (`usage_qty` * `unit_cost`).
* **`resources` table**: Stores resource metadata for enhanced context.
    -   `resource_id` (TEXT): A unique identifier for the resource.
    -   `owner` (TEXT): The email or name of the resource owner.
    -   `env` (TEXT): The environment (e.g., 'prod', 'dev', 'staging').
    -   `tags_json` (TEXT): A JSON string of key-value tags.

## 3. Technology Stack

-   **Backend**: FastAPI
-   **Database**: SQLite
-   **Vector Store**: ChromaDB
-   **LLM**: OpenAI GPT-4
-   **UI**: Streamlit
-   **Containerization**: Docker

## 4. Key Design Decisions

1.  **SQLite for Simplicity**: Chosen for rapid prototyping and local development due to its file-based nature. This avoids the complexity of setting up a separate database server.
2.  **ChromaDB for RAG**: Selected for its ease of setup and robust integration with LangChain. It is well-suited for a local, file-based vector store.
3.  **RAG Hybrid Context**: The RAG pipeline combines two distinct data sources for comprehensive answers: structured data (synthetic billing/resources from SQLite) and unstructured data (markdown reference files).
4.  **Recommendation Rule**: The **idle/underutilized resources** rule was chosen for its direct impact on cost savings and clear, heuristic-based logic.

## 5. RAG Prompting Strategy

The LLM is guided using a structured prompt with a few-shot learning approach.
-   **System Prompt**: The prompt defines the AI's role as a FinOps assistant, its primary function of answering questions based on context, and its constraints.
-   **Few-shot Examples**: The prompt includes examples for three key scenarios:
    -   **KPI Request**: Shows the model how to return a function name (e.g., `kpis.six_month_trend`) instead of attempting to calculate the value itself.
    -   **Recommendation Request**: Directs the model to return the name of the recommendations function and a brief explanation of its purpose.
    -   **General Q&A**: Illustrates how to answer standard questions using the provided context.
-   **Fallback Path**: If the LLM cannot find an answer in the provided context, the prompt instructs it to state it cannot answer the question and suggests checking the data.

## 6. Risks & Mitigation

| Risk | Mitigation Strategy |
| :--- | :--- |
| **Data Quality Issues** | Implement data validation rules at the ingestion stage to check for null values, negative costs, and duplicate resource IDs. |
| **LLM Costs** | Use smaller, more cost-effective models like `text-embedding-3-small` for embeddings. Implement caching for frequently asked questions to avoid redundant API calls. |
| **Prompt Injection** | Sanitize user inputs to prevent malicious prompts from manipulating the LLM's behavior. Filter outputs to ensure they adhere to the expected format. |
| **Performance with Large Data**| For larger datasets, migrate the `SQLite` database to `PostgreSQL` and deploy the application with sufficient computing resources. |