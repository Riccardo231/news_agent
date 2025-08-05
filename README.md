# Terminal News Agent

**Terminal News Agent** is the ultimate tool for reading, analyzing, and "dissecting" Google News headlines directly from your terminal.  
Not only can you browse the latest news, but you can launch **multiple local LLM agents** (via Ollama) to generate summaries, analyze implications, and build complex scenarios—all without a browser and with total privacy.

---

## 🚀 Features

- **Real news from Google News** in real-time (via RSS, no sketchy scraping)
- **Interactive terminal table** with keyboard navigation, Rich styling, and focus highlight
- **Global news summary** (one click, LLM-powered via Ollama)
- **Chained LLM agents:**
  - *Summary Agent*: concise, factual abstract
  - *Implications Agent*: in-depth analysis of consequences
  - *Theory Agent*: connects dots and builds scenarios
  - *Universal Analysis Agent*: multi-thematic framework for complex topics
  - *(All agents can be triggered from the terminal UI!)*
- **🔍 News Verification System** (with SerpAPI):
  - Verify selected articles or custom text
  - Fact-checking search results
  - Reliable sources cross-reference
  - AI-powered truth analysis
- **Open article in browser** with one key
- **Multi-language** and Google News topic filtering (configurable in settings)
- **No cloud required:**
  - 100% local processing, no external APIs needed
  - Ollama support out-of-the-box, just install and run
- **Designed for hacking/extending:** config/code separation, easy to customize
- **Works on Linux, macOS, WSL, Windows Terminal**

---

![Terminal Demo 1](./image/term_1.png)
![Terminal Demo 1](./image/term_2.png)
![Terminal Demo 2](./image/term_3.png)

---

## ⚡ Installation

Clone the repo and install locally:

```bash
git clone https://github.com/Pinperepette/news_agent.git
cd news_agent
pip install .

news-agent
```

## 🔧 Configuration

### Basic Settings

Edit `news_agent/settings.ini`:

```ini
[DEFAULT]
lang = it
topic = CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtbDBHZ0pKVkNnQVAB
articles_per_page = 15
model = qwen2:7b-instruct
ollama_url = http://localhost:11434/api/generate
serpapi_key = YOUR_SERPAPI_KEY_HERE
```

### News Verification Setup

To enable the news verification feature:

1. Get a free API key from [SerpAPI](https://serpapi.com/)
2. Add your key to `settings.ini`:
   ```ini
   serpapi_key = your_serpapi_key_here
   ```
3. The verification option (`v`) will appear in the menu

---

## 🎮 Usage

### Navigation
- **↑↓** Arrow keys: Navigate between articles
- **Enter**: Open selected article details
- **f**: Move to next article (auto-advance)
- **n/p**: Next/Previous page
- **Number**: Select specific article by number

### Actions
- **o**: Open article in browser
- **s**: Generate global summary
- **a**: Run LLM agents on selected article
- **v**: Verify news (if SerpAPI configured)
- **q**: Quit

### LLM Agents Menu (a)
1. **Riassunto**: Quick factual summary
2. **Implicazioni**: Social, economic, political consequences
3. **Teoria/Scenario**: Complex scenarios and connections
4. **Analisi Universale**: Multi-thematic framework for complex topics
5. **Tutti gli agenti**: Run all agents in sequence

### News Verification (v)
1. **Verify selected article**: Analyzes the currently selected news item
2. **Verify custom text**: Enter your own text to verify

The verification system:
- Searches for fact-checking information
- Cross-references with reliable sources
- Uses AI to analyze truthfulness
- Provides detailed verification report

---

## 🤖 LLM Agents

The system includes five specialized agents:

1. **Summary Agent**: Creates concise, factual summaries
2. **Implications Agent**: Analyzes social, economic, and political consequences
3. **Theory Agent**: Builds complex scenarios and connections
4. **Universal Analysis Agent**: Multi-thematic framework for complex topics
5. **Verification Agent**: Evaluates news truthfulness using multiple sources

### Universal Analysis Framework

The **Universal Analysis Agent** uses a structured methodology for analyzing complex topics:

- **Factual Analysis**: Identifies verifiable facts and context
- **Multi-dimensional Analysis**: Social, economic, political, technological, environmental dimensions
- **Critical Analysis**: Bias identification, credibility assessment, interest analysis
- **Forward-looking Analysis**: Probable scenarios, strategic implications, open questions
- **Methodological Synthesis**: Confidence levels and recommendations

This framework works on any complex topic and provides systematic, evidence-based analysis.

All agents run locally via Ollama - no cloud required!
