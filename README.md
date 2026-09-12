# tradeEngine

## Running the backend

The backend is a FastAPI app in `backend/` that uses relative imports, so it must be run as a package from the project root (this directory), with the `myenv` virtualenv active.

```bash
source backend/myenv/bin/activate
uvicorn backend.main:app --reload
```

- `--reload` restarts the server on file changes; drop it if you don't want that.
- The app connects to Interactive Brokers (TWS/IB Gateway) on startup via `backend/ibconnect.py` — make sure TWS/IB Gateway is running first, or the connection will fail.
- Once running, check `http://localhost:8000/api/status` to confirm the IB connection is live.
