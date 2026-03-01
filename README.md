# ATM Failure Intelligence System
[![Live Demo](https://img.shields.io/badge/Live-Demo-green)](https://your-streamlit-link.streamlit.app)
## 📌 Problem Statement
Automating troubleshooting of digital payment service issues (ATM downtime, technical declines) using historical data.

## 🚀 Current Version (v0.1)
- Synthetic ATM log dataset generation
- RandomForest classification model
- Evaluation using confusion matrix and classification report
- Feature importance analysis
- Root cause prediction function

## 🧠 Approach
1. Generate structured ATM logs
2. Train ML model to classify root causes:
   - Network_Issue
   - Server_Overload
   - Cash_Dispenser_Fault
   - Normal
3. Evaluate model performance
4. Improve class balance and feature engineering

## 📊 Model Performance
- Accuracy: ~99%
- Strong detection for network & server failures
- Currently improving hardware fault detection

## 🔜 Next Steps
- Improve dataset realism
- Add hardware signal feature
- Build Streamlit dashboard
- Add alert logic

---

Built as part of FinTech Cybersecurity Hackathon.