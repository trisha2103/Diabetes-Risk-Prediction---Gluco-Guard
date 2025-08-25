# app.py — "GlucoGuard" minimal-input diabetes risk calculator (stylish)

from pathlib import Path
import os, numpy as np, pandas as pd, joblib, streamlit as st

# ---------- Page & styles ----------
st.set_page_config(page_title="GlucoGuard — Diabetes Risk", page_icon="🩺", layout="centered")

st.markdown("""
<style>
/* Hide default Streamlit chrome (optional) */
#MainMenu {visibility: hidden;} footer {visibility: hidden;}

/* Hero banner */
.hero {
  padding: 1.2rem 1.4rem;
  border-radius: 18px;
  background: linear-gradient(135deg, #0ea5e9 0%, #22c55e 55%, #f59e0b 100%);
  color: #fff;
  margin: 0 0 16px 0;
  box-shadow: 0 10px 28px rgba(2,6,23,.25);
}
.hero h1 {font-size: 2.05rem; margin: 0 0 .25rem 0; letter-spacing:.2px;}
.hero p {margin: 0; opacity: .95}

/* Nice pill badge for result */
.pill {
  display:inline-block; padding:.38rem .75rem; border-radius:999px;
  font-weight:700; letter-spacing:.2px; color:#fff;
}

/* Card-ish form box */
.block-container {padding-top: 1.2rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>GlucoGuard ⚕️</h1>
  <p>Interactive diabetes risk estimator (BRFSS-based) — <em>educational use only</em></p>
</div>
""", unsafe_allow_html=True)

# ---------- Load model bundle ----------
APP_DIR = Path(__file__).resolve().parent
MODEL_PATH = APP_DIR / "model_diabetes_brfss.pkl"

try:
    bundle = joblib.load(MODEL_PATH)
except Exception as e:
    st.error(f"Failed to load {MODEL_PATH.name} — did you save the 7-feature model bundle?")
    st.exception(e)
    st.stop()

model    = bundle["model"]
FEATURES = bundle["features"]
thr_def  = float(bundle.get("threshold", 0.50))

EXPECTED = ["BMI","HighBP","HighChol","PhysActivity","GenHlth","Age","Sex"]
if sorted(FEATURES) != sorted(EXPECTED):
    st.error(f"Model was saved with features {FEATURES}, but the app expects {EXPECTED}. Retrain & save again.")
    st.stop()

# ---------- Friendly labels ----------
AGE_LABELS = {
    1:"18–24",2:"25–29",3:"30–34",4:"35–39",5:"40–44",
    6:"45–49",7:"50–54",8:"55–59",9:"60–64",10:"65–69",
    11:"70–74",12:"75–79",13:"80+"
}
GENHLTH_LABELS = {1:"Excellent",2:"Very good",3:"Good",4:"Fair",5:"Poor"}

# ---------- Sidebar controls ----------
st.sidebar.title("⚙️ Settings")
thr_user = st.sidebar.slider(
    "Decision threshold (probability ≥ classified as “At Risk”)",
    min_value=0.05, max_value=0.95, value=thr_def, step=0.01
)
st.sidebar.caption("Lower = more sensitive. Higher = more specific.")

# ---------- Input form (7 fields only) ----------
st.subheader("Enter your information")

with st.form("risk_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        BMI = st.number_input("BMI", min_value=10.0, max_value=80.0, value=28.0, step=0.1)
        HighBP = st.selectbox("High blood pressure? (0/1)", [0,1], index=0)
        HighChol = st.selectbox("High cholesterol? (0/1)", [0,1], index=0)
    with col2:
        PhysActivity = st.selectbox("Any physical activity in past 30 days? (0/1)", [0,1], index=1)
        GenHlth = st.selectbox("General health (1–5)", list(GENHLTH_LABELS.keys()),
                                index=2, format_func=lambda k: f"{k} – {GENHLTH_LABELS[k]}")
        Age = st.selectbox("Age group", list(AGE_LABELS.keys()),
                           index=7, format_func=lambda k: f"{k} – {AGE_LABELS[k]}")
        Sex = 0 if st.radio("Sex", ["Female","Male"], index=0, horizontal=True) == "Female" else 1

    submitted = st.form_submit_button("Predict")

# ---------- Predict & display ----------
if submitted:
    row = pd.DataFrame([[BMI, HighBP, HighChol, PhysActivity, GenHlth, Age, Sex]], columns=FEATURES)

    prob = float(model.predict_proba(row)[0,1])
    label = int(prob >= thr_user)

    band = "Low" if prob < 0.25 else "Moderate" if prob < 0.50 else "High" if prob < 0.75 else "Very High"
    pill_bg = "#10b981" if label == 0 else "#ef4444"   # green vs red

    st.markdown("---")
    cA, cB = st.columns([1,1])
    with cA:
        st.metric("Estimated probability", f"{prob:.3f}")
        st.caption(f"Decision threshold = {thr_user:.2f}")
    with cB:
        st.write("")
        st.markdown(f"<span class='pill' style='background:{pill_bg}'>"
                    f"{'Not at Risk (0)' if label==0 else 'At Risk (1)'} — {band}</span>",
                    unsafe_allow_html=True)

    # Visual risk bar
    st.progress(min(max(prob,0.0),1.0))

    st.caption("This calculator uses a logistic model trained on BRFSS survey features. "
               "It is for educational purposes and is **not** a medical diagnosis.")
    
# ---------- How it works (tiny footer) ----------
with st.expander("How this works"):
    st.markdown("""
    - We use 7 key inputs (BMI, blood pressure/cholesterol flags, physical activity, general health, age, sex).
    - A calibrated logistic model returns a probability; anything above your chosen threshold is labeled **At Risk**.
    - Tune the threshold in the left sidebar to prioritize sensitivity vs. specificity.
    """)
