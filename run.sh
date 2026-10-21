set -e
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo
echo " =============================================="
echo "  SBI-ADS  -  http://127.0.0.1:8000/dashboard"
echo " =============================================="
echo

exec uvicorn main:app --host 127.0.0.1 --port 8000
