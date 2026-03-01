from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd


#prediction function
def predict(latency, packet_loss, cpu_usage, transactions):
    pdf=pd.DataFrame({
        "latency": [latency],
        "packet_loss": [packet_loss],
        "cpu_usage": [cpu_usage],
        "transactions_last_5min": [transactions]
    }
    )
    return model.predict(pdf)[0]


df=pd.read_csv("atm_logs.csv")
x = df[["latency", "packet_loss", "cpu_usage", "transactions_last_5min"]]
y = df["root_cause"]

x_train,x_test,y_train,y_test =train_test_split(x,y,test_size=0.2,random_state=42)

model = RandomForestClassifier(class_weight="balanced",random_state=42)
model.fit(x_train,y_train)

accuracy=model.score(x_test,y_test)
print("model accuracy:",accuracy)

#calling prediction
predict(4200, 48, 60, 120)

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