import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import Dict
from fastapi import FastAPI,UploadFile,File,Websocket,WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pipeline import run_pipeline
load_dotenv()


jobs :Dict[str,dict] ={}
origin = ["http://localhost:3000"]
class ConnectionManager:
    def __init__(self):
        self.active: Dict[str,Websocket]={}



    async def connect(self,job_id:str,ws:Websocket):
        await ws.accept()
        self.active[job_id] = ws

    def disconnect(sel,job_id:str):
        self.active.pop(job_id,None)

    async def send(self,job_id:str,data:dict):
        ws = self.active.get(job_id)
        if ws:
            try:
                await ws.send_json(data)
            except:
                self.disconnect(job_id)

manager = ConnectionManager()  

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("TruthLens backend started")
    yield


app = FastAPI(title="TruthLens API",version="0.1.0",lifespan=lifespan)    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status":"TruthLens backend running"}
    

@app.post("/analyse")
async def analyse(file: UploadFile=File(...)):
    job_id = str(uuid.uuid4())
    contents = await file.read()
    jobs[job_id] = {"status": "pending","result":None}
    asyncio.create_task(
        run_pipeline(job_id,contents,file.filename or "upload",manager)

    )
    return {"job_id":job_id}



@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket:Websocket,job_id:str):
    await manager.connect(job_id,websocket) 
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(job_id)           

@app.get("/results/{job_id}")
async def get_result(job_id:str):
    job = jobs.get(job_id)
    if not job:
        return {"error":"job not found"}
    return job    