from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from app.api.routers import router
from app.infrastructure.persistence.database import init_db
from app.config import settings
import os

app = FastAPI(title=settings.app_name, docs_url="/api-docs", redoc_url="/redoc")

app.include_router(router, prefix="/api")


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def read_root():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


@app.get("/docs")
async def swagger_ui():
    html = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" type="text/css" href="/static/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="/static/swagger-ui-bundle.js"></script>
    <script>
    window.onload = function() {
        SwaggerUIBundle({
            url: "/openapi.json",
            dom_id: '#swagger-ui',
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.SwaggerUIStandalonePreset
            ]
        })
    }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html)


@app.get("/static/{filename}")
async def static_files(filename: str):
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", filename))


@app.get("/uploads/{filename}")
def get_file(filename: str):
    file_path = os.path.join(settings.upload_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)