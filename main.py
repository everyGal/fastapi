from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import subprocess
import json
import os

app = FastAPI()

class PSIRequest(BaseModel):
    sender_csv: str
    config_json: dict

@app.post("/psi")
def run_psi(req: PSIRequest):
    try:
        # Decode and save sender input
        with open("sender_input_file.csv", "w") as f:
            f.write(base64.b64decode(req.sender_csv).decode())

        # Save config JSON
        with open("config.json", "w") as f:
            json.dump(req.config_json, f)

        # Ensure receiver file exists
        if not os.path.exists("receiver_input_file.csv"):
            raise FileNotFoundError("receiver_input_file.csv missing")

        # Run PSI binary
        result = subprocess.run(
            ["./dpca_psi_example", "sender_input_file.csv", "receiver_input_file.csv", "--config", "config.json"],
            capture_output=True, text=True, check=True
        )

        # Parse last lines (placeholder logic)
        lines = result.stdout.strip().split("\n")
        audience_size = int(lines[-2])  # adjust this based on actual output format
        impressions = int(lines[-1])

        return {"audience_size": audience_size, "impressions": impressions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
