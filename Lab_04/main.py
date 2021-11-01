import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures


df = pd.read_csv("new.csv", delimiter=",")
df["result"].replace(["Win", "Lose"], [1, 0], inplace=True)
input_time_strings = df["time"].to_numpy()
time_list = []

for i in range(len(input_time_strings)):
    pt = datetime.strptime(input_time_strings[i], '%H:%M:%S.%f')
    total_seconds = pt.second + pt.minute * 60 + pt.hour * 3600 + pt.microsecond / 100000
    time_list.append(total_seconds)
df["time"] = pd.Series(np.array(time_list))
x = df[["result", "time"]].to_numpy()
y = df["score"].to_numpy()

train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.1)
poly_train_x = PolynomialFeatures(degree=3).fit_transform(train_x)
poly_test_x = PolynomialFeatures(degree=3).fit_transform(test_x)
model = LinearRegression()
model.fit(poly_train_x, train_y)

predict = model.predict(poly_test_x)
R2 = r2_score(test_y, predict)
print(f"R2 - {R2}")
fig, axes = plt.subplots(figsize=(6, 6))
axes.scatter(test_x[:, 1], test_y)
axes.scatter(test_x[:, 1], predict)
axes.set_xlabel("Час в секундах")
axes.set_ylabel("К-сть очок")
axes.set_title("Залежність к-сті очок від часу гри")
plt.show()


random_indexes = np.random.randint(0, len(train_x), size=5)
poly_future_data = PolynomialFeatures(degree=3).fit_transform(train_x[random_indexes])
predict = model.predict(poly_future_data)

print(train_x[random_indexes])
print(predict)

with open("predicted.csv", "w") as file:
    for i, inputs in enumerate(train_x[random_indexes]):
        state = "Win" if inputs[0] == 1 else "Lose"
        line = f"{state},{inputs[1]},{predict[i]}\n"
        file.write(line)