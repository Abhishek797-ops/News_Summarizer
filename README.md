# 📰 News Summarizer & Bias Detector

## 📌 Overview
This project is an **AI-powered News Summarizer & Bias Detector** that allows users to input a **news article URL** or **paste raw text**.  
The app then:
- **Summarizes the article** into simple and clear language.  
- Provides **different summary tones**:
  - 🟢 Neutral Summary  
  - 📑 Fact-only Summary  
  - 👶 Explain Like I’m 10  
- **Analyzes bias** by detecting tone and sentiment across multiple sources, highlighting whether the content leans **positive, negative, or neutral**.  

The goal is to make news more **accessible, unbiased, and easy to understand**.

---

## 🚀 Features
- ✅ Input via **URL** or **pasted text**
- ✅ Summarization in **different styles** (Neutral, Fact-only, Explain like 10)
- ✅ **Bias detection** using sentiment analysis
- ✅ Easy-to-read summaries for all audiences
- ✅ Web-based interactive UI 
- ✅ **NEW: Interactive Bias Slider** meter indicating Left, Center, or Right alignments

---

## 🛠️ Tech Stack
- **Frontend:** HTML, CSS, JavaScript (Tailwind CSS)
- **Backend:** Python, Flask
- **Libraries & Tools:**
  - `requests` → Fetch news content from URLs  
  - `BeautifulSoup` → Extract article text  
  - `google-generativeai` → **Gemini 2.5 Flash** for Summarization Model  
  - `nltk` / `textblob` / `vaderSentiment` → Sentiment & bias analysis (`python-dotenv` with hot-reload override integration) 

---

## 📂 Project Structure
├── app.py # Main application file (runs the summarizer & bias detector)
├── requirements.txt # Python dependencies
├── Procfile # Deployment configuration
├── templates/ # HTML templates for the web interface
├── README.md # Project documentation


## 🔮 Future Improvements

🌐 Multi-language support
📊 Cross-source trend comparison
🧩 Browser extension for on-page bias detection
