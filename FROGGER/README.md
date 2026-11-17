# FROGGER V1

Project 7 · HHL · Local GORGON API

Open this folder in VS Code. In PowerShell, with Python 3.12 installed:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1
```

Open [the dashboard](http://127.0.0.1:8000) and enter the absolute path to a copy of your artwork directory. Start with existing color folders. FROGGER moves matching root-level originals into those folders before processing the originals already there. It writes separate PNGs under each color folder's `No BG` directory and reuses existing outputs. If you edit an original and want it regenerated, remove its existing output first.

The first image that needs processing may trigger a U²-Net model download. Results, including per-file successes, skips, and errors, are saved to `reports/<job-id>.json`.

GORGON can submit `{"folder":"C:/Artwork/KillerBear"}` to `POST /api/jobs` and poll `GET /api/jobs/{job_id}` for progress and results. `GET /api/health` and `GET /api/gorgon/status` expose service status. The dashboard emits `gorgon:bot-event` as it polls. Run one local server process; there is one active job at a time and live job state resets on restart. Keep the service on loopback until authentication, directory restrictions, and a persistent worker are in place. The parent GORGON dashboard and additional presets are outside this build.

Run the engine smoke test with `python -m unittest discover -s tests` from this folder. It uses a stand-in for the background model so the workflow can be checked without downloading model weights.
