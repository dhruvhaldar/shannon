import uvicorn
from fastapi.staticfiles import StaticFiles
from api.index import app

# Mount static files
app.mount("/", StaticFiles(directory="public", html=True), name="public")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
