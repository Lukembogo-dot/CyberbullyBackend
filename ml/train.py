import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

# 1. Setup Paths
# This ensures it saves into your ml/ folder correctly
DATA_PATH = 'data/training.1600000.processed.noemoticon.csv'
MODEL_SAVE_PATH = 'ml/model.pkl'

# 2. Load and Balance Data
print("Loading dataset...")
cols = ['sentiment', 'id', 'date', 'query', 'user', 'text']
df_full = pd.read_csv(DATA_PATH, encoding='latin-1', names=cols)

print("Balancing classes...")
df_neg = df_full[df_full['sentiment'] == 0].sample(100000, random_state=42)
df_pos = df_full[df_full['sentiment'] == 4].sample(100000, random_state=42)

df_balanced = pd.concat([df_neg, df_pos]).sample(frac=1).reset_index(drop=True)
df_balanced['label'] = df_balanced['sentiment'].replace(4, 1) # 0=Toxic, 1=Safe

# 3. Split Data
X = df_balanced['text']
y = df_balanced['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Define and Train Pipeline
print("Training model... this might take a minute.")
model_pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1,2), max_features=50000, stop_words='english')),
    ('classifier', LogisticRegression(max_iter=1000))
])

model_pipeline.fit(X_train, y_train)

# 5. Evaluate
print("\nModel Performance:")
predictions = model_pipeline.predict(X_test)
print(classification_report(y_test, predictions))

# 6. Save the model (The "Loot")
# Check if ml directory exists, if not, create it
if not os.path.exists('ml'):
    os.makedirs('ml')

joblib.dump(model_pipeline, MODEL_SAVE_PATH)
print(f"\n✅ Success: Model saved to {MODEL_SAVE_PATH}")

# 7. Quick Test Function
def quick_test(text):
    pred = model_pipeline.predict([text])[0]
    prob = model_pipeline.predict_proba([text])[0]
    label = "🚩 TOXIC" if pred == 0 else "✅ SAFE"
    print(f"[{label}] {text} ({prob[pred]*100:.1f}% confidence)")

print("\nRunning test samples:")
quick_test("You are so helpful, thank you!")
quick_test("I really hate you, go away.")