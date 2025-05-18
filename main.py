from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import subprocess
import json
import os
import uuid
from typing import Dict

app = FastAPI()

class PSIRequest(BaseModel):
    sender_csv: str          # base64-encoded sender list
    receiver_csv: str        # base64-encoded receiver list
    config_json: Dict        # DPCA-PSI config blob

@app.post("/psi")
def run_psi(req: PSIRequest):
    """
    Runs DPCA-PSI on the two CSV inputs and returns a JSON result.
    Each request is fully self-contained → no data persistence between runs.
    """
    uid = str(uuid.uuid4())[:8]              # short random suffix
    sender_file   = f"sender_{uid}.csv"
    receiver_file = f"receiver_{uid}.csv"
    config_file   = f"config_{uid}.json"

    try:
        # 1️⃣  Decode & write the two CSVs
        with open(sender_file,   "w") as f:
            f.write(base64.b64decode(req.sender_csv).decode())

        with open(receiver_file, "w") as f:
            f.write(base64.b64decode(req.receiver_csv).decode())

        # 2️⃣  Write the JSON config
        with open(config_file, "w") as f:
            json.dump(req.config_json, f)

        # 3️⃣  Call the binary
        cmd = [
            "./dpca_psi_example",
            sender_file,
            receiver_file,
            "--config", config_file
        ]

        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )

        # 4️⃣  Parse the output
        # 👉 customise this parsing to your binary’s real format
        lines = [l for l in result.stdout.splitlines() if l.strip()]
        audience_size = int(lines[-2])
        impressions   = int(lines[-1])

        return {
            "audience_size": audience_size,
            "impressions":   impressions
        }

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500,
                            detail=f"PSI binary failed: {e.stderr or e.stdout}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 5️⃣  Always tidy up temp files
        for f in (sender_file, receiver_file, config_file):
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
