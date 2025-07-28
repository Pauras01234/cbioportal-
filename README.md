# 🧬 cBioPortal Chatbot

An LLM-powered chatbot that understands natural language questions and analyzes **LUAD (Lung Adenocarcinoma)** mutation and clinical data from cBioPortal.

Built using:

- Local LLM (Mistral or Phi via Ollama)
- Python
- LUAD clinical + mutation dataset

---

## 🗂 Project Structure

- `data/` - Processed mutation & expression files  
- `luad_tcga/` - Extracted mutation & clinical TSV files  
- `luad_tcga.tar` - Compressed archive of LUAD dataset  
- `chatbot.py` - Main chatbot runner  
- `llm_handler.py` - Parses user queries with local LLM  
- `data_loader.py` - Loads and preprocesses LUAD data  
- `data_queries.py` - Answers questions using the data  
- `db_config.py` - Database config (if applicable)  
- `test.py` - CLI test for chatbot  
- `test_llm_handler.py` - LLM parser unit tests  

---

## 🚀 How to Run

1. **Clone the repo**:

```bash
git clone https://github.com/Pauras01234/cbioportal-
cd cbioportal-
```

2. **Install requirements**:

```bash
pip install -r requirements.txt
```

3. **Run the chatbot**:

```bash
python chatbot.py
```

4. **Sample queries**:

- `Top 10 mutated genes`
- `How many patients have EGFR mutations?`
- `mRNA expression of TP53`
- `Genes with more than 50 mutations`

---

## 🤖 Features

- Understands plain English questions
- Handles gene mutation counts, top genes, expression summaries, and patient stats
- Runs offline using a local LLM

---

## 📊 Data Source

- Study: LUAD (Lung Adenocarcinoma, TCGA)
- Source: [https://www.cbioportal.org/study/summary?id=luad_tcga](https://www.cbioportal.org/study/summary?id=luad_tcga)

---

## 👤 Author

**Pauras Raut**  
MSc in Genomic Data Science  
[LinkedIn Profile](https://www.linkedin.com/in/pauras-raut-369a511aa/)

---

## 📄 License

Open-source under the [MIT License](https://opensource.org/licenses/MIT)
