from fastapi import FastAPI
from src.routes import ChatRoutes, FactsExtractorRoutes

app = FastAPI(title="Chats processing module")

app.include_router(ChatRoutes.router, prefix="/chat", tags=["chat"])
app.include_router(FactsExtractorRoutes.router, prefix="/facts", tags=["facts"])