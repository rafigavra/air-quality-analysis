## Setup Environment

### 1. Clone repository
```bash
git clone https://github.com/rafigavra/air-quality-analysis
cd air-quality-analysis
```

### 2. Buat virtual environment
```bash
python -m venv venv
```

### 3. Aktifkan virtual environment
```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Jalankan dashboard
```bash
streamlit run dashboard/dashboard.py
```