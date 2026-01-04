import fastapi
from routes import index_router, data_router

app = fastapi.FastAPI(
    title="NLP Algorithm API",
    description="API for NLP algorithm services",
    version="1.0.0"
)

# 包含路由
app.include_router(index_router)
app.include_router(data_router)

if __name__ == '__main__':
    import uvicorn
    app.debug = True
    uvicorn.run(app, host="0.0.0.0", port=3000,)
