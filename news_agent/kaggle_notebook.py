#!/usr/bin/env python

import os
import webbrowser
import tempfile
from pathlib import Path

def create_kaggle_notebook():
    """Creates a Kaggle notebook template for downloading and running AI models"""
    
    notebook_content = '''<!-- filepath: kaggle_news_agent.ipynb -->
<VSCode.Cell language="markdown">
# News Agent with Kaggle AI Models

This notebook helps you download and run AI models from Kaggle for news analysis.
Follow these steps to set up your environment and integrate with the news agent.
</VSCode.Cell>

<VSCode.Cell language="python">
# Install required packages
!pip install kaggle transformers torch accelerate bitsandbytes
!pip install rich beautifulsoup4 requests feedparser
</VSCode.Cell>

<VSCode.Cell language="markdown">
## 1. Setup Kaggle API

First, you need to configure your Kaggle API credentials:
1. Go to https://www.kaggle.com/account
2. Create a new API token (kaggle.json)
3. Upload the file using the file upload in the next cell
</VSCode.Cell>

<VSCode.Cell language="python">
# Upload your kaggle.json file and configure API
import os
from pathlib import Path

# Create .kaggle directory
kaggle_dir = Path.home() / '.kaggle'
kaggle_dir.mkdir(exist_ok=True)

# You need to upload kaggle.json file to the current directory first
# Then run this cell to move it to the correct location
import shutil
if os.path.exists('kaggle.json'):
    shutil.move('kaggle.json', kaggle_dir / 'kaggle.json')
    os.chmod(kaggle_dir / 'kaggle.json', 0o600)
    print("✅ Kaggle API configured successfully!")
else:
    print("❌ Please upload your kaggle.json file first")
</VSCode.Cell>

<VSCode.Cell language="markdown">
## 2. Browse Available Models

Popular AI models available on Kaggle for text analysis:
</VSCode.Cell>

<VSCode.Cell language="python">
# Search for available AI models
import subprocess
import json

def search_kaggle_models(query="language model"):
    """Search for models on Kaggle"""
    try:
        result = subprocess.run(['kaggle', 'models', 'list', '-s', query], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("🔍 Available models:")
            print(result.stdout)
        else:
            print("❌ Error searching models:", result.stderr)
    except Exception as e:
        print(f"❌ Error: {e}")

# Search for popular models
search_kaggle_models("llama")
search_kaggle_models("mistral")
search_kaggle_models("gemma")
</VSCode.Cell>

<VSCode.Cell language="markdown">
## 3. Download a Model

Select and download a model. Here are some popular choices:
</VSCode.Cell>

<VSCode.Cell language="python">
# Download a specific model (example with Llama)
import subprocess

def download_model(model_path):
    """Download a model from Kaggle"""
    try:
        print(f"📥 Downloading {model_path}...")
        result = subprocess.run(['kaggle', 'models', 'download', model_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Model downloaded successfully!")
            return True
        else:
            print("❌ Error downloading:", result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Example downloads (uncomment the one you want)
# download_model("microsoft/DialoGPT-medium")
# download_model("google/gemma-2b")
# download_model("mistralai/Mistral-7B-v0.1")

print("💡 Uncomment one of the download_model lines above to download a model")
</VSCode.Cell>

<VSCode.Cell language="markdown">
## 4. Load and Test the Model

Load the downloaded model and test it:
</VSCode.Cell>

<VSCode.Cell language="python">
# Load and test the model
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Configuration - update these paths based on your downloaded model
MODEL_PATH = "./microsoft-diaglogpt-medium"  # Update this path
MODEL_NAME = "microsoft/DialoGPT-medium"     # Update this name

def load_model(model_path, model_name):
    """Load the model and tokenizer"""
    try:
        print(f"🔄 Loading model from {model_path}...")
        
        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        print("✅ Model loaded successfully!")
        return tokenizer, model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None, None

def test_model(tokenizer, model, text="Analyze this news: Italy wins the World Cup"):
    """Test the model with sample text"""
    if tokenizer is None or model is None:
        print("❌ Model not loaded")
        return
    
    try:
        # Encode input
        inputs = tokenizer.encode(text, return_tensors="pt")
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + 100,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode output
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"📝 Input: {text}")
        print(f"🤖 Response: {response}")
        
    except Exception as e:
        print(f"❌ Error testing model: {e}")

# Load and test the model (uncomment when ready)
# tokenizer, model = load_model(MODEL_PATH, MODEL_NAME)
# test_model(tokenizer, model)
</VSCode.Cell>

<VSCode.Cell language="markdown">
## 5. Create News Agent Interface

Create a simple interface to analyze news with your Kaggle model:
</VSCode.Cell>

<VSCode.Cell language="python">
# News Agent Interface
import requests
from xml.etree import ElementTree as ET
import re
import html

def fetch_google_news(lang="it", topic=""):
    """Fetch news from Google RSS"""
    feed_url = f"https://news.google.com/rss?hl={lang}&gl={lang.upper()}&ceid={topic}"
    
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
        
        root = ET.fromstring(response.text)
        articles = []
        
        for item in root.findall('.//item'):
            title = item.findtext('title', '')
            link = item.findtext('link', '')
            pubDate = item.findtext('pubDate', '')
            description = item.findtext('description', '')
            source_el = item.find('source')
            author = source_el.text if source_el is not None else ""
            
            # Clean text
            clean_descr = re.sub('<[^<]+?>', '', description)
            clean_descr = html.unescape(clean_descr)
            clean_title = html.unescape(title)
            
            articles.append({
                "title": clean_title.strip(),
                "date": pubDate.strip(),
                "author": author.strip(),
                "summary": clean_descr.strip(),
                "link": link.strip(),
            })
        
        return articles
    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return []

def analyze_news_with_kaggle_model(article, tokenizer, model):
    """Analyze news article with the Kaggle model"""
    if tokenizer is None or model is None:
        return "❌ Model not loaded"
    
    # Create analysis prompt
    prompt = f"""Analyze this news article:
Title: {article['title']}
Summary: {article['summary'][:200]}
Author: {article['author']}

Provide a brief analysis covering:
1. Main facts
2. Potential implications
3. Credibility assessment
"""
    
    try:
        inputs = tokenizer.encode(prompt, return_tensors="pt", truncate=True, max_length=512)
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + 200,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the prompt from response
        analysis = response[len(prompt):].strip()
        return analysis if analysis else "🤖 Analysis completed (check model compatibility)"
        
    except Exception as e:
        return f"❌ Error analyzing: {e}"

# Example usage
print("🔄 Fetching latest news...")
articles = fetch_google_news("it")

if articles:
    print(f"📰 Found {len(articles)} articles")
    
    # Show first few articles
    for i, article in enumerate(articles[:3]):
        print(f"\n📄 Article {i+1}:")
        print(f"Title: {article['title']}")
        print(f"Author: {article['author']}")
        print(f"Summary: {article['summary'][:100]}...")
        
        # Analyze with model (uncomment when model is loaded)
        # analysis = analyze_news_with_kaggle_model(article, tokenizer, model)
        # print(f"🤖 Analysis: {analysis}")
else:
    print("❌ No articles found")
</VSCode.Cell>

<VSCode.Cell language="markdown">
## 6. Integration with Local News Agent

To integrate this with your local news agent, you can:

1. **Export the model**: Save the model in a format compatible with your local setup
2. **Create API endpoint**: Run a simple Flask/FastAPI server to serve the model
3. **Update settings**: Configure your local news agent to use this Kaggle model

Here's how to create a simple API:
</VSCode.Cell>

<VSCode.Cell language="python">
# Create a simple API server for the model
from flask import Flask, request, jsonify
import threading
import time

app = Flask(__name__)

# Global variables for model
global_tokenizer = None
global_model = None

@app.route('/analyze', methods=['POST'])
def analyze_endpoint():
    """API endpoint for news analysis"""
    try:
        data = request.json
        article_text = data.get('text', '')
        
        if not article_text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Analyze with loaded model
        analysis = analyze_news_with_kaggle_model(
            {'title': data.get('title', ''), 'summary': article_text, 'author': data.get('author', '')},
            global_tokenizer, 
            global_model
        )
        
        return jsonify({'analysis': analysis})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'model_loaded': global_model is not None})

def start_api_server():
    """Start the API server"""
    global global_tokenizer, global_model
    
    # Load model into global variables
    # global_tokenizer, global_model = load_model(MODEL_PATH, MODEL_NAME)
    
    print("🚀 Starting API server on http://localhost:5000")
    print("📝 Endpoints:")
    print("  - POST /analyze: Analyze news text")
    print("  - GET /health: Check server status")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

# Uncomment to start the API server
# start_api_server()

print("💡 Uncomment the last line to start the API server")
print("🔗 You can then configure your local news agent to use: http://localhost:5000/analyze")
</VSCode.Cell>

<VSCode.Cell language="markdown">
## 7. Local Integration Instructions

To use this Kaggle model with your local news agent:

1. **Update settings.ini**:
   ```ini
   provider = kaggle
   kaggle_api_url = http://localhost:5000/analyze
   ```

2. **Add to ai_providers.py**:
   ```python
   class KaggleProvider(AIProvider):
       def __init__(self, api_url):
           self.api_url = api_url
       
       def generate(self, prompt, max_tokens=2048):
           response = requests.post(self.api_url, json={'text': prompt})
           return response.json().get('analysis', 'Error')
   ```

3. **Update create_ai_provider function** to handle kaggle provider

4. **Start this notebook's API server** and your local news agent will use the Kaggle model!
</VSCode.Cell>'''

    return notebook_content

def open_kaggle_notebook():
    """Creates and opens a Kaggle notebook in the browser"""
    from rich.console import Console
    console = Console()
    
    try:
        # Create notebook content
        notebook_content = create_kaggle_notebook()
        
        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        notebook_path = Path(temp_dir) / "kaggle_news_agent.ipynb"
        
        # Save notebook
        with open(notebook_path, 'w', encoding='utf-8') as f:
            f.write(notebook_content)
        
        console.print(f"[green]✅ Notebook creato: {notebook_path}[/green]")
        console.print(f"[cyan]🔗 Apro Kaggle in browser...[/cyan]")
        
        # Open Kaggle in browser
        webbrowser.open("https://www.kaggle.com/code")
        
        console.print(f"[yellow]📝 Per usare il notebook:[/yellow]")
        console.print(f"[white]1. Carica il file: {notebook_path}[/white]")
        console.print(f"[white]2. Oppure copia il contenuto e incollalo in un nuovo notebook[/white]")
        console.print(f"[white]3. Segui le istruzioni nel notebook per configurare l'AI[/white]")
        
        return str(notebook_path)
        
    except Exception as e:
        console.print(f"[red]❌ Errore creando notebook: {e}[/red]")
        return None
