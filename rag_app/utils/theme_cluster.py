from typing import List, Dict
from langchain_openai.embeddings import OpenAIEmbeddings
from langfuse import get_client
from langfuse.openai import openai
from sklearn.cluster import KMeans
from .llm_retry import extractor_retry_or_none

langfuse = get_client()
embeddings_model = OpenAIEmbeddings()  # Utilisation de la nouvelle classe

# Prompt template to label clusters
LABEL_PROMPT = '''You are an academic assistant.\
Given these paper titles and their clustered keywords, provide a concise theme label for this group.'''  

def cluster_themes(texts: List[str], n_clusters: int = 5) -> Dict[int, List[int]]:
    """
    Cluster document embeddings into theme groups.
    Returns mapping of cluster_id to list of text indices.
    """
    embs = embeddings_model.embed_documents(texts)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embs)
    clusters = {}
    for idx, label in enumerate(labels):
        clusters.setdefault(label, []).append(idx)
    return clusters

@extractor_retry_or_none
def label_cluster(texts: List[str], cluster_indices: List[int]) -> str:
    """
    Use LLM to generate a label for a cluster of paper titles/texts.
    """
    subset = [texts[i] for i in cluster_indices]
    prompt = LABEL_PROMPT + "\n\n" + " ".join(subset)
    response = openai.chat.completions.create(
        model='gpt-4',
        messages=[{'role':'user','content':prompt}],
        name="theme_labeling_request"
    )
    return response.choices[0].message.content.strip()


def thematic_synthesizer(texts: List[str], n_clusters: int = 5) -> Dict[str, List[str]]:
    """
    Cluster paper titles/texts and return theme labels mapping to lists of member texts.
    """
    clusters = cluster_themes(texts, n_clusters=n_clusters)
    themed = {}
    for cid, indices in clusters.items():
        label = label_cluster(texts, indices)
        themed[label] = [texts[i] for i in indices]
    return themed