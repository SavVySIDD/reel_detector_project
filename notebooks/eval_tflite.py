# notebooks/eval_tflite.py
import json, numpy as np, pandas as pd
import tensorflow as tf
from sklearn.metrics import classification_report

scaler = json.load(open('../models/scaler.json'))
features = scaler['features']
mean = np.array(scaler['mean'])
std = np.array(scaler['std'])

# Update the path below to use your real windows CSV
df = pd.read_csv('../data/windows_labeled_synthetic.csv')
X_raw = df[features].values.astype(np.float32)
Xn = (X_raw - mean) / std
y = df['label'].values

interpreter = tf.lite.Interpreter(model_path='../models/model_quant.tflite')
interpreter.allocate_tensors()
inp = interpreter.get_input_details()[0]
outp = interpreter.get_output_details()[0]

preds = []
for i in range(Xn.shape[0]):
    x = Xn[i:i+1].astype(np.float32)
    interpreter.set_tensor(inp['index'], x)
    interpreter.invoke()
    out = interpreter.get_tensor(outp['index'])[0][0]
    preds.append(out)

y_pred = (np.array(preds) > 0.5).astype(int)
print(classification_report(y, y_pred))
