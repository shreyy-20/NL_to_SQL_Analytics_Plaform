from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import farmers, queries

app = FastAPI(title="KrishiQuery API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(farmers.router)
app.include_router(queries.router)


@app.get("/")
def health_check():
    return {"status": "KrishiQuery API is running"}


@app.on_event("startup")
def startup():
    print("🚀 Backend started")


@app.on_event("shutdown")
def shutdown():
    print("🛑 Backend stopped")