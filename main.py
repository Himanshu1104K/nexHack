from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from src import *
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

logger = get_logger(__name__)
db_user = None
db_teacher = None
teacher_store = None
user_store = None
chat_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_user, db_teacher, teacher_store, user_store,chat_graph

    try:
        try:
            cred = credentials.Certificate(CREDENTIALS)
            logger.info("✅ Firebase initialization successful with CREDENTIALS")
        except Exception as e:
            logger.error(f"❌ Firebase initialization failed: {str(e)}")
            raise
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        db_user = db.collection(USER_DATABASE_NAME)
        db_teacher = db.collection(TEACHER_DATABASE_NAME)

        teacher_store = await setup_teacher_store()
        user_store = await setup_user_store()

        chat_graph = await get_chat_graph()

        yield
    except Exception as e:
        raise e
    finally:
        pass


# FastAPI application
app = FastAPI(
    title="NexHack API",
    description="API for NexHack which acts as a mediator",
    version="1.0.0",
    lifespan=lifespan,
)

for router in [auth.router]:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
