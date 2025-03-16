from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, field_validator
from typing import Optional
import subprocess
import json
import base64

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Script Generator API",
    description="API for generating movie loglines from abstracts",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScriptRequest(BaseModel):
    title: str
    genre: str
    logline: str 
    central_message: str 
    main_character_profiles: str 
    supporting_charcter_profiles: str 
    abstract: str

    # Your field validators remain the same...

@app.post("/script-agent/")
async def generate_script(request: ScriptRequest):
    try:
        # Prepare the data as JSON
        script_data = {
            "title": request.title,
            "genre": request.genre,
            "logline": request.logline,
            "central_message": request.central_message,
            "main_character_profiles": request.main_character_profiles,
            "supporting_charcter_profiles": request.supporting_charcter_profiles,
            "abstract": request.abstract
        }
        
        # Encode the data to prevent issues with special characters
        script_data_json = json.dumps(script_data)
        encoded_data = base64.b64encode(script_data_json.encode()).decode()
        
        # Build a Python command that sets each attribute individually
        python_code = (
            "import json, base64;"
            "from src.demo_flow.main import PoemFlow;"
            f"data = json.loads(base64.b64decode('{encoded_data}').decode());"
            "pf = PoemFlow();"
            # Set each attribute individually
            "pf.state.title = data['title'];"
            "pf.state.genre = data['genre'];"
            "pf.state.logline = data['logline'];"
            "pf.state.central_message = data['central_message'];"
            "pf.state.main_character_profiles = data['main_character_profiles'];"
            "pf.state.supporting_charcter_profiles = data['supporting_charcter_profiles'];"
            "pf.state.abstract = data['abstract'];"
            # Initialize empty lists
            "pf.state.book = [];"
            "pf.state.book_outline = [];"
            # Run the flow
            "result = pf.kickoff();"
            "print(result if isinstance(result, str) else json.dumps(result))"
        )

        # Run the command
        proc = subprocess.run(
            ["python", "-c", python_code],
            capture_output=True,
            text=True
        )

        if proc.returncode != 0:
            raise Exception(proc.stderr)
        
        # Get the result
        output = proc.stdout
        
        # Try to parse as JSON if possible
        try:
            result = json.loads(output)
            script_content = result.get('content', output)
        except json.JSONDecodeError:
            script_content = output
        
        filename = f"{request.title.replace(' ', '_')}_script.txt"

        return Response(
            content=script_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to Script Generator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
