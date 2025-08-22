# notebooks/train_and_convert.py
# Train baseline and MLP, convert to quantized TFLite, save scaler.json
import os, sys, json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import tensorflow as tf
from tensorflow import keras

def load_windows_csv(path):
    df = pd.read_csv(path)
    if 'label' not in df.columns:
        raise ValueError("CSV must contain 'label' column.")
    return df

def normalize_save(X, out_path):
    mean = X.mean(axis=0)
    std = X.std(axis=0) + 1e-9
    Xn = (X - mean) / std
    scaler = {'mean': mean.tolist(), 'std': std.tolist(), 'features': list(X.columns)}
    with open(out_path, 'w') as f:
        json.dump(scaler, f)
    return Xn, scaler

def train_rf(X_train, y_train, X_test, y_test):
    print('[RF] Training baseline...')
    rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    preds = rf.predict(X_test)
    print('[RF] Test report:\n', classification_report(y_test, preds))
    return rf

def train_mlp(X_train, y_train, X_val, y_val, input_dim, epochs=25):
    print('[MLP] Training model...')
    model = keras.Sequential([
        keras.layers.Input(shape=(input_dim,)),
        keras.layers.Dense(64, activation='relu'),
        keras.layers.Dropout(0.2),
        keras.layers.Dense(32, activation='relu'),
        keras.layers.Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, batch_size=64, verbose=2)
    return model

def convert_to_tflite(model, X_calib, out_path):
    print('[TFLite] Converting and quantizing...')
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    def rep_gen():
        for i in range(min(200, X_calib.shape[0])):
            yield [X_calib[i:i+1].astype(np.float32)]
    converter.representative_dataset = rep_gen
    tflite_model = converter.convert()
    with open(out_path,'wb') as f:
        f.write(tflite_model)
    print('[TFLite] Saved:', out_path)

def eval_tflite(tflite_path, X_test, y_test):
    print('[TFLite] Running local eval...')
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()
    inp = interpreter.get_input_details()[0]
    outp = interpreter.get_output_details()[0]
    preds = []
    for i in range(X_test.shape[0]):
        x = X_test[i:i+1].astype(np.float32)
        interpreter.set_tensor(inp['index'], x)
        interpreter.invoke()
        out = interpreter.get_tensor(outp['index'])[0][0]
        preds.append(out)
    y_pred = (np.array(preds) > 0.5).astype(int)
    print('[TFLite] Report:\n', classification_report(y_test, y_pred))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python train_and_convert.py ../data/windows_labeled.csv')
        sys.exit(1)
    csv_path = sys.argv[1]
    df = load_windows_csv(csv_path)
    X = df.drop(columns=[c for c in ['wstart'] if c in df.columns] + ['label'])
    y = df['label'].values

    os.makedirs('../models', exist_ok=True)
    Xn, scaler = normalize_save(X, '../models/scaler.json')
    X_train_val, X_test, y_train_val, y_test = train_test_split(Xn, y, test_size=0.2, random_state=42, stratify=y)
    X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.125, random_state=42, stratify=y_train_val)
    print('Shapes:', X_train.shape, X_val.shape, X_test.shape)

    # Baseline (train on raw X for RF)
    X_raw = X.values
    # align splits for quick baseline (simplified)
    rf = train_rf(X_raw[:len(X_train_val)], y_train_val, X_raw[-len(X_test):], y_test)

    model = train_mlp(X_train, y_train, X_val, y_val, input_dim=X_train.shape[1], epochs=25)
    model.save('../models/model.h5')
    convert_to_tflite(model, X_train, '../models/model_quant.tflite')
    eval_tflite('../models/model_quant.tflite', X_test, y_test)
    print('Saved scaler.json and models in ../models/')
