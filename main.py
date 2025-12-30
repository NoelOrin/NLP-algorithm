import fastapi
import routes.users as users

app = fastapi.FastAPI()

app.include_router(users.router)
