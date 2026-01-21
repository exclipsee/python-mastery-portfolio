import streamlit as st

st.set_page_config(page_title="PM Portfolio Demo", layout="wide")

st.title("Python Mastery Portfolio — Live Demo")
st.write("Small demo app that queries the local API and visualizes simple embeddings.")

api_mode = st.sidebar.selectbox("API Mode", ["testclient", "http"])
api_url = st.sidebar.text_input("API base URL (for http mode)", "http://127.0.0.1:8000")

use_testclient = api_mode == "testclient"

if use_testclient:
    from fastapi.testclient import TestClient

    from python_mastery_portfolio.api import app

    client = TestClient(app)
else:
    import requests


# Simple API examples
st.header("API Examples")
col1, col2 = st.columns(2)
with col1:
    n = st.number_input("Fibonacci n", min_value=0, value=20, step=1)
    if st.button("Get Fibonacci"):
        if use_testclient:
            r = client.get(f"/fib/{n}")
            st.json(r.json())
        else:
            r = requests.get(f"{api_url}/fib/{n}")
            st.json(r.json())

with col2:
    a = st.number_input("GCD a", value=48, step=1)
    b = st.number_input("GCD b", value=18, step=1)
    if st.button("Compute GCD"):
        if use_testclient:
            r = client.get("/math/gcd", params={"a": a, "b": b})
            st.json(r.json())
        else:
            r = requests.get(f"{api_url}/math/gcd", params={"a": a, "b": b})
            st.json(r.json())

# Embeddings demo
st.header("Embeddings / Semantic Search Demo")

default_docs = [
    "FastAPI is a modern, fast web framework for building APIs with Python.",
    "Pandas provides powerful data structures for data analysis in Python.",
    "Scikit-learn offers simple and efficient tools for predictive data analysis.",
    "Sentence Transformers allows easy computation of dense vector representations for sentences.",
]

docs_text = st.text_area("Documents (one per line)", value="\n".join(default_docs), height=200)
query = st.text_input("Query", value="How to build an API in Python?")

docs: list[str] = [d.strip() for d in docs_text.splitlines() if d.strip()]

use_transformers = st.checkbox("Prefer sentence-transformers if available", value=True)

if st.button("Run semantic search"):
    try:
        if use_transformers:
            import numpy as np
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer("all-MiniLM-L6-v2")
            doc_emb = model.encode(docs, convert_to_numpy=True)
            q_emb = model.encode([query], convert_to_numpy=True)[0]
            sims = (doc_emb @ q_emb) / (
                np.linalg.norm(doc_emb, axis=1) * np.linalg.norm(q_emb) + 1e-12
            )
            ranked = sims.argsort()[::-1]
            st.write("Using dense sentence-transformers embeddings")
            for i in ranked:
                st.write(f"score={sims[i]:.4f} — {docs[i]}")

        else:
            raise ImportError("force TF-IDF")
    except Exception:
        st.write("Falling back to TF-IDF")
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vect = TfidfVectorizer().fit_transform(docs + [query])
        sims = cosine_similarity(vect[-1], vect[:-1])[0]
        ranked = sims.argsort()[::-1]
        for i in ranked:
            st.write(f"score={sims[i]:.4f} — {docs[i]}")

    # Simple bar chart
    try:
        import pandas as pd

        scores = [float(sims[i]) for i in ranked]
        labels = [docs[i][:80] + ("..." if len(docs[i]) > 80 else "") for i in ranked]
        df = pd.DataFrame({"score": scores}, index=labels)
        st.bar_chart(df)
    except Exception:
        pass

st.markdown("---")
st.write(
    "Tips: start the API with `uvicorn python_mastery_portfolio.api:app --reload` to use HTTP mode."
)
