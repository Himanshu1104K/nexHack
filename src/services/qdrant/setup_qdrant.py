from qdrant_client import QdrantClient

from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from src.core.configs import (
    QDRANT_HOST,
    QDRANT_API_KEY,
    TEACHER_COLLECTION_NAME,
    USER_COLLECTION_NAME,
)


# Initialize Qdrant client
client = QdrantClient(
    url=QDRANT_HOST,
    api_key=QDRANT_API_KEY,
)


async def setup_teacher_store():
    """Initialize and return the teacher vector store"""
    # Create collection if it doesn't exist
    if not client.collection_exists(TEACHER_COLLECTION_NAME):
        client.create_collection(
            collection_name=TEACHER_COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )

    # Create vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = QdrantVectorStore(
        client=client, collection_name=TEACHER_COLLECTION_NAME, embedding=embeddings
    )

    return vectorstore


async def setup_user_store():
    """Initialize and return the user vector store"""
    # Create collection if it doesn't exist
    if not client.collection_exists(USER_COLLECTION_NAME):
        client.create_collection(
            collection_name=USER_COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )

    # Create vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = QdrantVectorStore(
        client=client, collection_name=USER_COLLECTION_NAME, embedding=embeddings
    )

    return vectorstore
