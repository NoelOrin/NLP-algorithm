import fastapi
from server.routes import index_router, data_router

app = fastapi.FastAPI(
    title="NLP Algorithm API",
    description="API for NLP algorithm services",
    version="1.0.0"
)

# 包含路由
app.include_router(index_router)
app.include_router(data_router)
