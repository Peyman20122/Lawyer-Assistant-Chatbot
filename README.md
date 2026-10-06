# LRABot — Legal Research Assistant (UAE Labor Law, RAG)

A RAG-based quick research tool designed to help lawyers or legal consultants retrieve
key points from the **UAE ​​Labor Law** (Federal Decree-Law No. 33 of 2021
and its amendments), providing a link to the official source for every answer.

##  How to use this tool safely

- This is a **quick research aid**; it is not a substitute for reading the full
official text of the legislation or consulting a licensed lawyer.
- Every answer is **paraphrased** and not a verbatim quote from the law (due
to copyright restrictions on official texts and translations). Always verify
the original article before relying on it for actual legal work.
- The knowledge base covers **350 topics** derived from authentic research using
official sources (MOHRE, u.ae, uaelegislation.gov.ae) and reliable legal
references; however, its scope is limited and does not cover every detail
of the legislation. ## Project Structure

```
lawyer_assistant/
├── lawyer_assistant_chatbot.py   # Entry point — run this file
├── knowledge_base.json           # 350 legal topics, each with its source
├── requirements.txt
├── .env                          # API key and model settings (never share this file)
└── .gitignore
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Open the `.env` file and enter your API key:

```
LLM_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
# LLM_BASE_URL=   # Only if using a provider other than OpenAI
```

## Running the Application

```bash
python lawyer_assistant_chatbot.py
```

Type your legal question to receive an answer along with a list of retrieved sources. Type
`خروج` (Exit) to end the session.

Example questions to try:
- "How is the end-of-service gratuity calculated?"
- "What are the grounds for dismissal without notice or severance pay?"
- "What is the deadline for filing a cassation appeal?"
- "What is the ruling on inheritance cases?" (To test the "out-of-scope" response)

## Answers with Sources

Each response consists of two parts: the answer itself (based solely on the retrieved context,
not the model's general knowledge) and a list of "Retrieved Sources." This list includes
the topic, reference article, source name, and link—allowing you to immediately verify
the original text. ## Running without an API Key

If `LLM_API_KEY` is left blank, the tool continues to function—displaying the raw
snippets retrieved from the knowledge base directly, without natural language
formulation.

## Using Another Provider

OpenAI is the default. To use another OpenAI-compatible provider (such as
DeepSeek or OpenRouter), set both variables in `.env`:

```
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com
```

Use only the provider's official domain. Never point `LLM_BASE_URL` to an
unknown third-party domain.

## Expanding the Knowledge Base

Each entry in `knowledge_base.json` follows this structure:

```json
{
"id": "l001",
"topic": "Employment contract duration",
"article_ref": "Article regarding contract duration -- Federal Decree-Law No. 33 of 2021",
"text": "A summary of the topic in your own words, not a verbatim quote from the law",
"source_name": "Source name",
"source_url": "Official source link"
}
```

When adding new topics, adhere to the same rule: first find an official or
reliable source, summarize in your own words, and always cite the source. Do
not invent figures or legal provisions without verification.

## Configuring Retrieval Behavior

In the `lawyer_assistant_chatbot.py` file:

- `TOP_K` -- The number of topics retrieved per question (default is 3). - `SIMILARITY_THRESHOLD` -- The similarity score required to consider a question
within the scope of the knowledge base (default: 0.35). Lower it to expand coverage,
or raise it to reduce responses to questions that are not clearly relevant.

## Deployment

It runs as a standard Python script and can easily be integrated with a web interface
(FastAPI/Flask) or any platform that executes Python processes. Always keep
`LLM_API_KEY` as a platform-level secret, and do not upload the `.env` file to any repository.

## Known Limitations

- The knowledge base does not cover every detail of labor law, nor does it cover
other areas of law (civil, criminal, commercial) at all.
- There is no authentication or audit logging system to track users and their queries; 
implement this before actual organizational use.
- Legislation changes through subsequent amendments; the knowledge base reflects
a general understanding based only on the time of its creation.
