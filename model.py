from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import random
import time
import json


#simulating live atm
def simulate_live_data(num_atms=5):
    live_data = []
    
    for i in range(1, num_atms + 1):
        atm_data = {
            "atm_id": f"ATM_{i}",
            "latency": random.randint(100, 5000),
            "packet_loss": random.randint(0, 60),
            "cpu_usage": random.randint(20, 100),
            "transactions_last_5min": random.randint(10, 500)
        }
        live_data.append(atm_data)
    
    return live_data


def train_model(df):
    x = df[["latency", "packet_loss", "cpu_usage", "transactions_last_5min"]]
    y = df["root_cause"]
    
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42
    )
    
    model = RandomForestClassifier(class_weight="balanced", random_state=42)
    model.fit(x_train, y_train)
    
    return model, x_test, y_test,x,y




df=pd.read_csv("atm_logs.csv")
model,x_test,y_test,x,y=train_model(df)

accuracy=model.score(x_test,y_test)
print("model accuracy:",accuracy)


y_pred= model.predict(x_test)
print("confusion matrix")
print(confusion_matrix(y_test,y_pred)) #original confusion matrix

print("classification report")
print(classification_report(y_test,y_pred,zero_division=0))

cm=confusion_matrix(y_test,y_pred) #to print without confusion gives conf matrix without confusion
cdf=pd.DataFrame(
    cm,
    index=model.classes_,
    columns=model.classes_
)
print(cdf)

importance=pd.DataFrame({
    "Feature": x.columns,
    "Importance": model.feature_importances_
})
importance=importance.sort_values(by="Importance",ascending=False)
print(importance)




with open("severity_config.json", "r") as f:
    severity_weight = json.load(f)
atm_failure_history = {}    
atm_escalated = {}
while True:
    atms = simulate_live_data(num_atms=5)
    
    print("\n--- Monitoring Cycle ---")
    
    for atm in atms:
        atm_id = atm["atm_id"]

        df_live = pd.DataFrame([{
            "latency": atm["latency"],
            "packet_loss": atm["packet_loss"],
            "cpu_usage": atm["cpu_usage"],
            "transactions_last_5min": atm["transactions_last_5min"]
        }])

        prediction = model.predict(df_live)[0]
        probabilities = model.predict_proba(df_live)[0]
        confidence = max(probabilities)

        # Initialize counter if not exists
        current_time = time.time()

        if atm_id not in atm_failure_history:
            atm_failure_history[atm_id] = []

        if prediction != "Normal" and confidence > 0.7:
            weight = confidence * severity_weight.get(prediction, 1)  # between 0 and 1
            atm_failure_history[atm_id].append((current_time, weight))

        # Remove failures older than 10 seconds (demo window)
        atm_failure_history[atm_id] = [
            (t, w) for (t, w) in atm_failure_history[atm_id]
            if current_time - t <= 10
        ]
        risk_score = sum(w for (_, w) in atm_failure_history[atm_id])

        print(f"\nATM: {atm_id}")
        print("Prediction:", prediction)
        print("Confidence:", round(confidence * 100, 2), "%")
        print("Risk Score (last 10 sec):", round(risk_score, 2))

        if risk_score >= 2.5:
            if not atm_escalated.get(atm_id, False):
                print("🚨 ESCALATED: Technician Dispatch Required")
                atm_escalated[atm_id] = True
        else:
            atm_escalated[atm_id] = False   
    
    time.sleep(3)