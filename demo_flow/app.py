from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, field_validator
from typing import Optional
import subprocess
import json
import base64
import os
import tempfile
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
        # Create a safe filename
        safe_filename = request.title.replace(' ', '_').replace('/', '_').replace('\\', '_')
        output_file = f"{safe_filename}_script.txt"
        
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
        
        # Encode the data to base64 to avoid command line issues
        encoded_data = base64.b64encode(json.dumps(script_data).encode()).decode()
        
        # Construct the Python code
        python_code = f"""
import json, base64, sys, os
from src.demo_flow.main import PoemFlow
data = json.loads(base64.b64decode('{encoded_data}').decode())
pf = PoemFlow()
pf.state.title = data['title']
pf.state.genre = data['genre']
pf.state.logline = data['logline']
pf.state.central_message = data['central_message']
pf.state.main_character_profiles = data['main_character_profiles']
pf.state.supporting_charcter_profiles = data['supporting_charcter_profiles']
pf.state.abstract = data['abstract']
pf.state.book = []
pf.state.book_outline = []
result = pf.kickoff()
with open('{output_file}', 'w', encoding='utf-8') as f:
    f.write(result)
print('Script saved to {output_file}')
"""
        
        # Set the working directory to the root of the project
        working_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Run the Python script with the -c flag
        proc = subprocess.run(
            ["python", "-c", python_code],
            capture_output=True,
            text=True,
            env=os.environ.copy(),  # Ensure environment variables are passed
            # cwd=working_directory  # Set the working directory
        )
        
        if proc.returncode != 0:
            error_message = proc.stderr
            raise Exception(f"Script generation failed: {error_message}")
        
        # Check if the file exists
        if not os.path.exists(output_file):
            raise Exception(f"File {output_file} was not created. Process output: {proc.stdout}")
        
        # Read the file content
        with open(output_file, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        return Response(
            content=script_content,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={output_file}"}
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
