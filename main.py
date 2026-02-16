from fastapi import FastAPI,HTTPException,Request
import logging
from fastapi.middleware.cors import CORSMiddleware
from routers import project_router,finance_router,auth_router,user_router
from routers import info_router,report_router,ws_routes

print("Main module loaded")


app = FastAPI()

import logging
from fastapi import FastAPI, Request

# Create a logger for your app
logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)  # or DEBUG
logger.propagate = True  # important so logs go to Uvicorn handlers

# Optional: add a handler if you want to control formatting
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI()

# Middleware to log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception:
        logger.exception("Unhandled exception")
        raise
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(finance_router.router)
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(info_router.router)
app.include_router(report_router.router)
app.include_router(project_router.router)
app.include_router(ws_routes.router)

@app.get("/",summary="Default landing route")
def landing():
    return {"status":"OK","message":"Hello World"}
        
