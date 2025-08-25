# GlucoGuard — Diabetes Risk (BRFSS)

Minimal-input Streamlit app that estimates diabetes risk from 7 survey-style features
(BMI, HighBP, HighChol, PhysActivity, GenHlth, Age, Sex). **Educational use only** — not a medical device.

## Run locally
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
