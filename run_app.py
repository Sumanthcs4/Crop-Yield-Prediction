import subprocess
import time
import sys
# Launch FastAPI backend
fastapi_process = subprocess.Popen(["uvicorn", "app:app", "--reload"])

# Wait a moment for backend to start
time.sleep(2)

# Launch Streamlit frontend
streamlit_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "streamlit_app/app.py"])
# Optional: wait for both to complete (block until they are killed)
try:
    fastapi_process.wait()
    streamlit_process.wait()
except KeyboardInterrupt:
    print("Shutting down...")
    fastapi_process.terminate()
    streamlit_process.terminate()
