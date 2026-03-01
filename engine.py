import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def train_model():
    df = pd.read_csv("atm_logs.csv")

    x = df[["latency", "packet_loss", "cpu_usage", "transactions_last_5min"]]
    y = df["root_cause"]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(class_weight="balanced", random_state=42)
    model.fit(x_train, y_train)

    return model

def load_severity():
    with open("severity_config.json", "r") as f:
        return json.load(f)

def predict_atm(model, severity_weight, atm_data):
    df_live = pd.DataFrame([{
        "latency": atm_data["latency"],
        "packet_loss": atm_data["packet_loss"],
        "cpu_usage": atm_data["cpu_usage"],
        "transactions_last_5min": atm_data["transactions_last_5min"]
    }])

    prediction = model.predict(df_live)[0]
    confidence = max(model.predict_proba(df_live)[0])
    severity = severity_weight.get(prediction, 1)

    risk_score = confidence * severity

    return prediction, confidence, risk_score