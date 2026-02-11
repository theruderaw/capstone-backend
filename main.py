from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import finance_service,auth_router,user_router,info_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(finance_service.router)
app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(info_router.router)


@app.get("/",summary="Default landing route")
def landing():
    return {"status":"OK","message":"Hello World"}
        
