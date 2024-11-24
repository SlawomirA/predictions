import uvicorn
from fastapi import FastAPI
from src.router.router import router as main_router
app = FastAPI()

app.include_router(main_router)

@app.get("/", tags=["Health check"])
async def health_check():
    return {
        "name": "Data scraping API",
        "type": "scraper-api",
        "description": "The software that scrapes quotes on request",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import cx_Oracle
    print(cx_Oracle.clientversion())
    uvicorn.run(app, host="127.0.0.1", port=8087)
