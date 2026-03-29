py -m pip install -r requirements.txt
Start-Process "http://127.0.0.1:8000"
py -m uvicorn src.aether.main:app --host 0.0.0.0 --port 8000 --reload
pause