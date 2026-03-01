import random
import pandas as pd

records = []

for i in range(1000):
    atm_id = f"atm_{random.randint(1,10)}"
    latency = random.randint(100, 5000)
    packet_loss = random.randint(0, 60)
    cpu_usage = random.randint(20, 100)
    transactions_last_5min = random.randint(10, 500)
    dispenser_health = random.randint(0,100)

    if packet_loss > 40 and latency > 3000:
        root_cause = "Network_Issue"
        error_code = 68

    elif cpu_usage > 85 and transactions_last_5min > 300:
        root_cause = "Server_Overload"
        error_code = 91

    elif dispenser_health < 20:
        root_cause = "Cash_Dispenser_Fault"
        error_code = 55

    else:
        root_cause = "Normal"
        error_code = 0

    records.append({
        "atm_id": atm_id,
        "latency": latency,
        "packet_loss": packet_loss,
        "cpu_usage": cpu_usage,
        "transactions_last_5min": transactions_last_5min,
        "error_code": error_code,
        "root_cause": root_cause
    })

df = pd.DataFrame(records)

# 🔥 Save to CSV
df.to_csv("atm_logs.csv", index=False)

print("CSV file created successfully!")