### 🧾 Prerequisites
- Python 3.10+
- Git
- pip or pipenv (recommended)
- (Optional) Virtual environment tool like `venv` or `virtualenv`

---

### 🌀 Step-by-step Setup

```bash
# 1️⃣ Clone the repository
git clone https://github.com/JavierBL89/Home-Ventilation-Predictor.git
cd Home-Ventilation-Predictor

# 2️⃣ Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# 3️⃣ Install dependencies
pip install -r requirements.txt

# 4️⃣ Run the Flask server
python server.py


🖥️ Open the App
After the server is running, open your browser and go to:
http://127.0.0.1:5000/