"""
Entry point for running the API module directly
"""

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run("sloptimize.api.main:app", host="127.0.0.1", port=8000, reload=True)