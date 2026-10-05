from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import faiss
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import SentenceTransformer

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_BASE_PATH = BASE_DIR / "knowledge_base.json"
EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
TOP_K = 3
SIMILARITY_THRESHOLD = 0.35

LLM_API_KEY = os.environ.get("LLM_API_KEY")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL")  # leave unset for the real OpenAI endpoint

SYSTEM_PROMPT = (
    "أنت مساعد بحث قانوني تقني (وليس محامياً) موجّه لمحامين محترفين. "
    "أجب على سؤال المحامي باستخدام المعلومات الموجودة في السياق القانوني "
    "المقدم لك فقط. لا تخترع أي رقم أو حكم غير موجود في السياق. اذكر رقم "
    "المادة المرجعية إن وُجدت في السياق. إذا كان السياق لا يغطي السؤال "
    "بوضوح، قل صراحة إن هذا خارج نطاق القاعدة المعرفية المحدودة لهذه الأداة "
    "وينبغي الرجوع للنص الرسمي الكامل. أجب بالعربية الفصحى، بدقة واختصار."
)

OUT_OF_SCOPE_MESSAGE = (
    "لم يتم العثور على موضوع ذي صلة واضحة في القاعدة المعرفية المحدودة لهذه الأداة.\n"
    "يرجى الرجوع مباشرة إلى uaelegislation.gov.ae أو استشارة المصدر الرسمي."
)

ERROR_MESSAGE = "عذراً، حدثت مشكلة في الوصول إلى خدمة الذكاء الاصطناعي الآن. يرجى المحاولة مرة أخرى بعد قليل."


def load_knowledge_base() -> list[dict]:
    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class LegalResearchAssistant:
    def __init__(self, kb: list[dict], index, embedder: SentenceTransformer) -> None:
        self.kb = kb
        self.index = index
        self.embedder = embedder
        self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL) if LLM_API_KEY else None

    def search(self, question: str) -> str:
        query_vec = self.embedder.encode([question], convert_to_numpy=True, normalize_embeddings=True)
        scores, indices = self.index.search(query_vec.astype(np.float32), TOP_K)

        if scores[0][0] < SIMILARITY_THRESHOLD:
            return OUT_OF_SCOPE_MESSAGE

        retrieved = [self.kb[idx] for idx in indices[0] if idx != -1]
        context_block = "\n\n".join(
            f"[{r['topic']} -- {r['article_ref']}]\n{r['text']}" for r in retrieved
        )

        if not self.client:
            lines = ["(LLM_API_KEY غير مضبوط -- عرض المقتطفات الخام فقط)\n"]
            lines += [f"- [{r['topic']}] {r['text']}" for r in retrieved]
            answer = "\n".join(lines)
        else:
            try:
                response = self.client.chat.completions.create(
                    model=LLM_MODEL,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"سؤال المحامي: {question}\n\nالسياق القانوني:\n{context_block}"},
                    ],
                    temperature=0.1,
                )
                answer = response.choices[0].message.content
            except Exception as exc:
                print(f"[LLM error] {exc}")
                return ERROR_MESSAGE

        sources = "\n".join(
            f"  - {r['topic']} ({r['article_ref']})\n"
            f"    المصدر: {r['source_name']}\n"
            f"    الرابط: {r['source_url']}"
            for r in retrieved
        )
        return f"الإجابة:\n\n{answer}\n\nالمصادر المسترجَعة:\n{sources}"


def build_assistant() -> LegalResearchAssistant:
    kb = load_knowledge_base()
    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

    texts = [f"{entry['topic']} ({entry['article_ref']}): {entry['text']}" for entry in kb]
    vectors = embedder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors.astype(np.float32))

    return LegalResearchAssistant(kb, index, embedder)


def main() -> None:
    assistant = build_assistant()

    print("LRABot: مرحباً أيها المستخدم الكريم")
    print("LRABot: مساعد البحث القانوني جاهز")
    print("LRABot: اكتب سؤالك أدناه (اكتب 'خروج' لإنهاء المحادثة)\n")

    while True:
        question = input("سؤالك: ").strip()
        if question.lower() == "خروج":
            break
        if not question:
            continue
        print()
        print("LRABot:")
        print(assistant.search(question))
        print()


if __name__ == "__main__":
    main()
