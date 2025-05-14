# Project Setup Guide

1. **Clone the Repository**
   - Clone the repo to your local machine:
     ```bash
     git clone https://github.com/yourusername/FireSense.git
     cd FireSense
     ```

2. **Set up the Virtual Environment**
   - Create and activate the virtual environment:
   
     On macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
     
     On Windows:
     ```bash
     python -m venv venv
     .\venv\Scripts\activate
     ```

3. **Install Dependencies**
   - With the virtual environment active, install dependencies:
     ```bash
     pip install -r requirements.txt
     ```

4. **Freeze Dependencies (when adding new ones)**
   - After installing new packages, update `requirements.txt`:
     ```bash
     pip freeze > requirements.txt
     ```

5. **Running the Project**
   - Make sure the virtual environment is active.
   - Run the project script (e.g., `main.py`):
     ```bash
     python main.py
     ```

6. **Deactivate the Virtual Environment**
   - When done, deactivate the environment:
     ```bash
     deactivate
     ```
