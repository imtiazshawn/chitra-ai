# AI Video Agent

A Python-based AI Video Agent project.

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   copy .env.example .env
   # Edit .env with your API keys
   ```

5. Run the project:
   ```bash
   python src/main.py
   ```

## Project Structure

```
ChitraAI/
├── venv/                 # Virtual environment
├── src/                  # Source code
│   └── main.py          # Entry point
├── requirements.txt      # Dependencies
├── .env.example         # Environment template
├── .gitignore           # Git ignore
└── README.md            # Documentation
```
