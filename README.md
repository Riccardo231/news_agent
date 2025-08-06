# Terminal News Agent

**Terminal News Agent** is the ultimate tool for reading, analyzing, and "dissecting" Google News headlines directly from your terminal.  
Not only can you browse the latest news, but you can launch **multiple AI agents** to generate summaries, analyze implications, and build complex scenarios—all with support for local (Ollama) and cloud (OpenAI, Claude) AI providers.

---

## 🚀 Features

- **Real news from Google News** in real-time (via RSS, no sketchy scraping)
- **Interactive terminal table** with keyboard navigation, Rich styling, and focus highlight
- **Multiple AI Providers**: Support for Ollama (local), OpenAI, and Claude
- **Chained LLM agents:**
  - *Summary Agent*: concise, factual abstract
  - *Implications Agent*: in-depth analysis of consequences
  - *Theory Agent*: connects dots and builds scenarios
  - *Universal Analysis Agent*: multi-thematic framework for complex topics
  - *(All agents can be triggered from the terminal UI!)*
- **🔍 News Verification System** (with SerpAPI):
  - Verify selected articles or custom text
  - Fact-checking search results with full content scraping
  - Reliable sources cross-reference
  - AI-powered truth analysis
- **Full article content scraping** for comprehensive analysis
- **Open article in browser** with one key
- **Multi-language** and Google News topic filtering (configurable in settings)
- **No cloud required:**
  - 100% local processing with Ollama, no external APIs needed
  - Cloud options available for higher quality analysis
- **Designed for hacking/extending:** config/code separation, easy to customize
- **Works on Linux, macOS, WSL, Windows Terminal**

---

![Terminal Demo 1](./image/term_1.png)
![Terminal Demo 1](./image/term_2.png)

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

### Quick Setup

#### 🚀 Fast Start with Claude (Recommended)
1. Get your Claude API key from [console.anthropic.com](https://console.anthropic.com/)
2. Edit `news_agent/settings.ini`:
   ```ini
   provider = claude
   claude_api_key = sk-ant-your-key-here
   ```
3. Run: `python -m news_agent.main`

#### 🏠 Local Setup with Ollama
1. Install [Ollama](https://ollama.ai/)
2. Run: `ollama pull qwen2:7b-instruct`
3. Edit `news_agent/settings.ini`:
   ```ini
   provider = ollama
   model = qwen2:7b-instruct
   ```
4. Run: `python -m news_agent.main`

### Detailed Configuration

Edit `news_agent/settings.ini`:

```ini
[DEFAULT]
lang = it
topic = https://www.ansa.it/sito/ansait_rss.xml
articles_per_page = 15
provider = ollama
model = qwen2:7b-instruct
ollama_url = http://localhost:11434/api/generate
serpapi_key = 
openai_api_key = 
claude_api_key = 
openai_model = gpt-4
claude_model = claude-3-5-sonnet-20241022
```

### 🤖 AI Provider System

The system uses a **factory pattern** that allows you to easily switch between different AI providers by changing just one line in the configuration.

#### How to Choose Your AI Provider

Simply change the `provider =` line in `settings.ini`:

```ini
# For Ollama (local, free)
provider = ollama

# For OpenAI (cloud, paid)
provider = openai

# For Claude (cloud, paid)
provider = claude
```

#### 1. Claude (Recommended - High Quality)
```ini
provider = claude
claude_api_key = sk-ant-your-claude-key-here
claude_model = claude-3-5-sonnet-20241022
```

**Available Claude Models:**
- `claude-3-opus-20240229` - Most powerful (expensive)
- `claude-3-5-sonnet-20241022` - Balanced (recommended)
- `claude-3-5-sonnet-20240926` - Alternative Sonnet
- `claude-3-5-haiku-20241022` - Fastest (cheapest)

- **Pros**: Excellent reasoning, high quality responses, best for complex analysis
- **Cons**: Requires API key, costs money (~$0.003/1K tokens)
- **Setup**: Get API key from [Anthropic Console](https://console.anthropic.com/)

#### 2. Ollama (Local - Free)
```ini
provider = ollama
model = qwen2:7b-instruct
ollama_url = http://localhost:11434/api/generate
```

**Recommended Models:**
- `qwen2:7b-instruct` - Good balance of speed and quality
- `llama3.2:3b` - Fast and lightweight
- `mistral:7b` - High quality for size
- `codellama:7b` - Good for technical topics

- **Pros**: Free, private, no internet required, no API limits
- **Cons**: Requires local setup, slower than cloud options
- **Setup**: Install Ollama and run `ollama pull qwen2:7b-instruct`

#### 3. OpenAI
```ini
provider = openai
openai_api_key = sk-your-openai-key-here
openai_model = gpt-4
```

**Available Models:**
- `gpt-4` - Most powerful (expensive)
- `gpt-3.5-turbo` - Good balance (cheaper)
- `gpt-4-turbo` - Latest GPT-4 version

- **Pros**: High quality, reliable, excellent for creative tasks
- **Cons**: Requires API key, costs money
- **Setup**: Get API key from [OpenAI Platform](https://platform.openai.com/)

### AI Provider Comparison

| Provider | Cost | Privacy | Quality | Speed | Setup |
|----------|------|---------|---------|-------|-------|
| **Claude** | Pay-per-use | Cloud | Excellent | Fast | API key |
| **Ollama** | Free | 100% Private | Good | Medium | Local install |
| **OpenAI** | Pay-per-use | Cloud | Excellent | Fast | API key |

### How the AI System Works

1. **Configuration Reading**: The program reads `provider =` from `settings.ini`
2. **Provider Creation**: Creates the appropriate AI provider using `create_ai_provider()`
3. **Unified Interface**: All agents use the same provider for:
   - 📰 Article summarization (`s`)
   - 🤖 LLM agents (`a`)
   - 🔍 News verification (`v`)
4. **Model Name Display**: Shows which model is being used in response titles

### News Verification Setup

To enable the news verification feature:

1. Get a free API key from [SerpAPI](https://serpapi.com/)
2. Add your key to `settings.ini`:
   ```ini
   serpapi_key = your_serpapi_key_here
   ```
3. The verification option (`v`) will appear in the menu

**Verification Features:**
- Searches for fact-checking information
- Cross-references with reliable sources
- **Scrapes full content** of verification articles
- Uses AI to analyze truthfulness
- Provides detailed verification report

---

## 🎮 Usage

### Navigation
- **↑↓** Arrow keys: Navigate between articles
- **w/z**: Alternative navigation keys
- **Enter**: Open selected article details
- **f**: Move to next article (auto-advance)
- **n/p**: Next/Previous page
- **Number**: Select specific article by number

### Actions
- **o**: Open article in browser
- **s**: Generate article summary (with full content scraping)
- **a**: Run LLM agents on selected article
- **v**: Verify news (if SerpAPI configured)
- **q**: Quit

### LLM Agents Menu (a)
1. **Riassunto**: Quick factual summary using full article content
2. **Implicazioni**: Social, economic, political consequences
3. **Teoria/Scenario**: Complex scenarios and connections
4. **Analisi Universale**: Multi-thematic framework for complex topics
5. **Tutti gli agenti**: Run all agents in sequence

### News Verification (v)
1. **Verify selected article**: Analyzes the currently selected news item
2. **Verify custom text**: Enter your own text to verify
3. **Validazione verità**: Direct truth validation with clear verdict

The verification system:
- Searches for fact-checking information
- Cross-references with reliable sources
- **Scrapes full content** of verification articles
- Uses AI to analyze truthfulness
- Provides detailed verification report with content status
- **NEW**: Direct truth validation with VERDICT (VERA/FALSA/DUBBIA)

---

## 🤖 LLM Agents

The system includes five specialized agents that work with **any AI provider**:

1. **Summary Agent**: Creates concise, factual summaries using full article content
2. **Implications Agent**: Analyzes social, economic, and political consequences
3. **Theory Agent**: Builds complex scenarios and connections
4. **Universal Analysis Agent**: Multi-thematic framework for complex topics
5. **Verification Agent**: Evaluates news truthfulness using multiple sources
6. **Truth Validation Agent**: Provides direct verdict (VERA/FALSA/DUBBIA) with confidence level

### Universal Analysis Framework

The **Universal Analysis Agent** uses a structured methodology for analyzing complex topics:

- **Factual Analysis**: Identifies verifiable facts and context
- **Multi-dimensional Analysis**: Social, economic, political, technological, environmental dimensions
- **Critical Analysis**: Bias identification, credibility assessment, interest analysis
- **Forward-looking Analysis**: Probable scenarios, strategic implications, open questions
- **Methodological Synthesis**: Confidence levels and recommendations

This framework works on any complex topic and provides systematic, evidence-based analysis.

### Truth Validation Agent

The **Truth Validation Agent** provides a direct and clear assessment of news truthfulness:

- **🎯 Direct Verdict**: [VERA] / [FALSA] / [DUBBIA] / [INSUFFICIENTI DATI]
- **📊 Confidence Level**: [ALTA] / [MEDIA] / [BASSA] 
- **🔍 Red Flags**: Identifies bias, suspicious sources, contradictions
- **✅ Confirmations**: Lists sources that support or contradict the news
- **📝 Clear Reasoning**: Explains the verdict with evidence

This agent is specifically designed to give users a clear, actionable assessment of whether a news item is true or false.

### Content Processing

**All agents now use full article content:**
- Articles are automatically scraped for complete text
- Fallback to RSS summary if scraping fails
- Google News links are properly resolved
- Content is cleaned and optimized for AI analysis

---

## 🔧 Advanced Configuration

### RSS Feed Configuration

You can use direct RSS feeds instead of Google News:

```ini
# Direct RSS feed (recommended for better scraping)
topic = https://www.ansa.it/sito/ansait_rss.xml

# Or Google News topic ID
topic = CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtbDBHZ0pKVkNnQVAB
```

### Language and Region

```ini
lang = it          # Language code (it, en, es, fr, de, etc.)
articles_per_page = 15  # Number of articles per page
```

### Model-Specific Settings

Each provider supports different models. Experiment to find the best for your use case:

```ini
# Ollama models
model = qwen2:7b-instruct
model = llama3.2:3b
model = mistral:7b

# OpenAI models
openai_model = gpt-4
openai_model = gpt-3.5-turbo

# Claude models
claude_model = claude-3-5-sonnet-20241022
claude_model = claude-3-5-haiku-20241022
```

---

## 🚀 Getting Started Examples

### Example 1: Quick Start with Claude
```ini
provider = claude
claude_api_key = sk-ant-your-key-here
claude_model = claude-3-5-sonnet-20241022
```

### Example 2: Local Setup with Ollama
```ini
provider = ollama
model = qwen2:7b-instruct
```

### Example 3: OpenAI Setup
```ini
provider = openai
openai_api_key = sk-your-key-here
openai_model = gpt-4
```

### Example 4: Full Configuration with Verification
```ini
provider = claude
claude_api_key = sk-ant-your-key-here
claude_model = claude-3-5-sonnet-20241022
serpapi_key = your_serpapi_key_here
topic = https://www.ansa.it/sito/ansait_rss.xml
```

All agents work with any provider - choose based on your needs for privacy, cost, and quality!
