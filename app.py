from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import json
import shutil
import sqlite3
import requests
import markdown
from datetime import datetime
import pytesseract
from PIL import Image
from dateutil import parser 
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() # Add this import at the top

# Set correct data directory
DATA_DIR = "C:\\Users\\DELL\\TDS\\prj1\\data" if os.name == "nt" else "/data"
os.makedirs(DATA_DIR, exist_ok=True)

# FastAPI app
app = FastAPI()

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Load OpenAI API Key
AIPROXY_TOKEN = ("eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDMxMDdAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.hljPAkh0ASP812vEV2LYkGWd600KAkhF60hzDoLUgAY")
if not AIPROXY_TOKEN:
    print("❌ ERROR: AIPROXY_TOKEN is NOT set in the environment!")
    raise HTTPException(status_code=500, detail="AIPROXY_TOKEN is missing. Set it in your environment variables.")
else:
    print(f"✅ AIPROXY_TOKEN is set: {AIPROXY_TOKEN[:5]}********")  


# Define the request model
class TaskRequest(BaseModel):
    task: str

# Helper function to run shell commands
def run_shell_command(command):
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        return result.stdout.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API to execute tasks
@app.post("/run")
def run_task(request: TaskRequest):
    task = request.task.lower()

    if "install uv" in task:
        try:
            run_shell_command("pip install uv")
            run_shell_command("uv run https://raw.githubusercontent.com/sanand0/tools-in-data-science-public/tds-2025-01/project-1/datagen.py user@example.com")
            return {"status": "success", "message": "Data generated successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    elif "format" in task and "prettier" in task:
        run_shell_command("npm install -g prettier@3.4.2")
        run_shell_command(f"prettier --write {DATA_DIR}/format.md")
        return {"status": "success", "message": "File formatted"}

    elif any(kw in task for kw in ["count wednesday", "number of wednesdays", "how many wednesdays"]):
        file_path = os.path.join(DATA_DIR, "dates.txt")
        output_path = os.path.join(DATA_DIR, "dates-wednesdays.txt")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Source file not found")

        with open(file_path, "r") as file:
            dates = file.readlines()

        wednesdays = 0
        for date in dates:
            date = date.strip()
            if not date:
                continue  # Skip empty lines
        
            try:
                parsed_date = parser.parse(date)  # Automatically detect format
                if parsed_date.weekday() == 2:  # 2 = Wednesday
                    wednesdays += 1
            except ValueError:
                print(f"Skipping invalid date format: {date}")  # Log the error

        with open(output_path, "w") as output_file:
            output_file.write(str(wednesdays))

        return {"status": "success", "message": "Wednesdays counted"}

    elif "sort contacts" in task:
        file_path = os.path.join(DATA_DIR, "contacts.json")
        output_path = os.path.join(DATA_DIR, "contacts-sorted.json")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Contacts file not found")

        with open(file_path, "r") as file:
            contacts = json.load(file)

        sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))

        with open(output_path, "w") as file:
            json.dump(sorted_contacts, file, indent=4)

        return {"status": "success", "message": "Contacts sorted"}

    elif "most recent logs" in task:
        log_dir = os.path.join(DATA_DIR, "logs")
        output_path = os.path.join(DATA_DIR, "logs-recent.txt")

        if not os.path.exists(log_dir):
            raise HTTPException(status_code=404, detail="Logs directory not found")

        log_files = sorted([f for f in os.listdir(log_dir) if f.endswith(".log")], reverse=True)
        log_contents = [open(os.path.join(log_dir, file)).readline().strip() for file in log_files[:10]]

        with open(output_path, "w") as file:
            file.writelines("\n".join(log_contents))

        return {"status": "success", "message": "Recent logs processed"}

    elif "extract markdown titles" in task:
        docs_dir = os.path.join(DATA_DIR, "docs")
        output_path = os.path.join(DATA_DIR, "docs/index.json")

        if not os.path.exists(docs_dir):
            raise HTTPException(status_code=404, detail="Docs directory not found")

        index = {}

        # Recursively search for Markdown files in all subfolders
        for root, _, files in os.walk(docs_dir):
            for file in files:
                if file.endswith(".md"):  # Only process markdown files
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, docs_dir)  # Store relative path

                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            if line.startswith("# "):  # Extract first H1 title
                                index[relative_path] = line.strip("# ").strip()
                                break  # Stop after the first H1

        # Save index to JSON file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Create directory if it doesn't exist
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(index, file, indent=4)

        return {"status": "success", "message": "Markdown index created"}

    # Change this part of your code for the email extraction task

    elif "extract email sender" in task:
        file_path = os.path.join(DATA_DIR, "email.txt")
        output_path = os.path.join(DATA_DIR, "email-sender.txt")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Email file not found")

        with open(file_path, "r") as file:
            email_content = file.read()

        # Extract sender using regex first - more reliable than LLM for this case
        import re
        sender_match = re.search(r'From:.*?<(.*?)>', email_content)
        if sender_match:
            sender = sender_match.group(1)
        else:
            # Fallback to LLM if regex fails
            response = requests.post(
                "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {AIPROXY_TOKEN}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "user", "content": "Extract only the sender's email address from this email header:\n" + email_content}
                    ],
                    "temperature": 0
                }
            )
            if 'choices' in response.json():
                sender = response.json()["choices"][0]["message"]["content"].strip()
            else:
                raise HTTPException(status_code=500, detail="Failed to extract email sender")

        with open(output_path, "w") as file:
            file.write(sender)

        return {"status": "success", "message": "Email sender extracted"}

    elif "extract credit card" in task:
        file_path = os.path.join(DATA_DIR, "credit_card.png")  # Changed hyphen to underscore
        output_path = os.path.join(DATA_DIR, "credit-card.txt")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Credit card image not found")

        try:
            # Convert to RGB if necessary
            image = Image.open(file_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Use tesseract to extract text
            text = pytesseract.image_to_string(image)
            
            # Extract only numbers
            card_number = ''.join(filter(str.isdigit, text))
            
            with open(output_path, "w") as file:
                file.write(card_number)

            return {"status": "success", "message": "Credit card number extracted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

    elif "sqlite query" in task:
        db_path = os.path.join(DATA_DIR, "ticket-sales.db")
        output_path = os.path.join(DATA_DIR, "ticket-sales-gold.txt")

        if not os.path.exists(db_path):
            raise HTTPException(status_code=404, detail="Database file not found")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(price * units) FROM tickets WHERE type='Gold'")
        total_sales = cursor.fetchone()[0]

        with open(output_path, "w") as file:
            file.write(str(total_sales))

        return {"status": "success", "message": "Sales calculated"}
    
    elif "similar comments" in task:
        file_path = os.path.join(DATA_DIR, "comments.txt")
        output_path = os.path.join(DATA_DIR, "comments-similar.txt")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Comments file not found")

        # Read comments
        with open(file_path, "r", encoding="utf-8") as file:
            comments = [line.strip() for line in file.readlines() if line.strip()]

        if len(comments) < 2:
            raise HTTPException(status_code=400, detail="Not enough comments to find similarities")

        try:
            # Debugging: Print OpenAI API Key
            print(f"OpenAI API Key: {AIPROXY_TOKEN}")

            # Get embeddings from AI Proxy
            response = requests.post(
                "https://aiproxy.sanand.workers.dev/openai/v1/embeddings",  # Correct endpoint
                headers={
                    "Authorization": f"Bearer {AIPROXY_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "text-embedding-3-small",
                    "input": comments
                }
            )

            # Debugging: Print API response
            print(f"API Response: {response.status_code}, {response.text}")

            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"Error from AI Proxy: {response.text}")

            # Extract embeddings
            embeddings = [item["embedding"] for item in response.json()["data"]]

            # Convert to numpy array for efficient computation
            import numpy as np
            embedding_array = np.array(embeddings)

            # Calculate cosine similarity
            # Normalize the vectors
            norms = np.linalg.norm(embedding_array, axis=1, keepdims=True)
            normalized_embeddings = embedding_array / norms

            # Compute similarity matrix
            similarity_matrix = np.dot(normalized_embeddings, normalized_embeddings.T)

            # Set diagonal to -inf to ignore self-similarity
            np.fill_diagonal(similarity_matrix, -np.inf)

            # Find most similar pair
            most_similar_pair = np.unravel_index(similarity_matrix.argmax(), similarity_matrix.shape)

            # Write the results
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(f"{comments[most_similar_pair[0]]}\n")
                file.write(f"{comments[most_similar_pair[1]]}\n")

            return {"status": "success", "message": "Most similar comments identified and saved"}

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing comments: {str(e)}")


    else:
        raise HTTPException(status_code=400, detail="Unknown task")

# API to read file contents
@app.get("/read")
def read_file(path: str):
    file_path = os.path.join(DATA_DIR, path)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(file_path, "r") as file:
        return file.read()