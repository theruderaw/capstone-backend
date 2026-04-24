from fastapi import FastAPI,HTTPException,Request
import logging
from fastapi.middleware.cors import CORSMiddleware
from routers import helmet_router,project_router,finance_router,auth_router,user_router,info_router,report_router
import ws

print("Main module loaded")

# Create a logger for your app
logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)  # or DEBUG
logger.propagate = True  # important so logs go to Uvicorn handlers

# Console handler for formatting
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# File handler to write logs to a file
file_handler = logging.FileHandler("server_requests.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(helmet_router.router)
app.include_router(ws.router)

@app.get("/",summary="Default landing route")
def landing():
    return {"status":"OK","message":"Hello World"}

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Outgoing response: {response.status_code}")
    return response