import pandas as pd
import numpy as np

rows = 100

data = {
    "customer_id":range(1,rows+1),
    "SEX":np.random.randint(1,3,rows),
    "EDUCATION":np.random.randint(1,4,rows),
    "MARRIAGE":np.random.randint(1,3,rows),
    "AGE":np.random.randint(21,65,rows),
    "LIMIT_BAL":np.random.randint(10000,500000,rows),
}

for col in ["PAY_0","PAY_2","PAY_3","PAY_4","PAY_5","PAY_6"]:
    data[col] = np.random.randint(-2,5,rows)

for i in range(1,7):
    data[f"BILL_AMT{i}"] = np.random.randint(0,100000,rows)
    data[f"PAY_AMT{i}"] = np.random.randint(0,50000,rows)

df = pd.DataFrame(data)

df.to_csv("data/test_customer_credit_data.csv",index=False)

print("Test data created")
