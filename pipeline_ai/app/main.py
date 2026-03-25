from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="Pipeline Intelligence Engine API",
    description="Agentic SDR system API managing intent, pitches, and sequencing.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Pipeline Intelligence Engine"}

# Future: include routers (e.g. app.include_router(sales_router))

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
