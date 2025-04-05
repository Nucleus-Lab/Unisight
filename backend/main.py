from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import canvas_router, user_router, message_router, visualization_router, mcp_router
from backend.database.init_db import init_db

# Initialize the database
init_db()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(canvas_router)
app.include_router(user_router)
app.include_router(message_router)
app.include_router(visualization_router)
app.include_router(mcp_router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)