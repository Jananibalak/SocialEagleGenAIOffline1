# 🗳️ Tamil Nadu Election Console Simulator (Python)

A beginner-friendly **Python console project** to practice **core Python fundamentals** using a real-world theme: **Tamil Nadu Election simulation**.

This program allows users to:
- Register voters
- Cast votes (one voter = one vote)
- View constituency-wise results
- View state-wide summary
- Save/load data using file handling

✅ Best suited for Python learners who want to strengthen fundamentals.

---

## 📌 Features

✅ **Voter Registration**
- Generates a unique Voter ID
- Checks age eligibility (>= 18)

✅ **Voting System**
- Allows vote only in voter’s constituency
- Prevents duplicate voting using `set`

✅ **Results**
- Constituency-wise winner report
- State-wide vote share report

✅ **Persistence**
- Saves voters and votes to text files

---

## 🧠 Concepts Covered (Python Fundamentals)

This project covers:

- ✅ Operators
- ✅ Datatypes
- ✅ Lists
- ✅ Tuples
- ✅ Sets
- ✅ Dictionaries
- ✅ Control Flow (`if`, `elif`, `else`)
- ✅ Nested If
- ✅ Loops (`for`, `while`)
- ✅ Functions
- ✅ Error Handling (`try/except`)
- ✅ File Handling (read/write/append)
- ✅ Importing packages (`random`, `datetime`)

---

## 🗂️ Project Structure

```
TN-Election-Simulator/
│
├── tn_election_simulator.py
├── voters.txt          # auto-created
├── votes.txt           # auto-created
└── README.md
```

---

## ⚙️ Requirements

- Python 3.x

✅ No external libraries required (only built-in modules).

---

## ▶️ How to Run

1. Download / clone the repository
2. Open terminal in the project folder
3. Run:

```bash
python tn_election_simulator.py
```

---

## 📋 Menu Options

When the program starts, you will see:

```
1. Register Voter
2. Cast Vote
3. View Constituency Results
4. State Summary
5. Reset Votes (Simulation)
6. Exit
```

---

## 📂 Data Files Used

### 📄 `voters.txt`
Stores registered voter details:

Format:
```
VOTER_ID,NAME,AGE,CONSTITUENCY
```

Example:
```
TNJA456154812,Janani,28,Salem
```

---

### 📄 `votes.txt`
Stores votes cast:

Format:
```
VOTER_ID,CONSTITUENCY,CANDIDATE
```

Example:
```
TNJA456154812,Salem,DMK
```

---

## 🧑‍💻 Sample Output

### 🧾 Registration
```
✅ Registration successful!
Your Voter ID: TNJA456154812
Constituency: Salem
```

### 🗳️ Casting Vote
```
✅ Vote cast successfully for DMK!
```

### 📊 Constituency Result
```
Constituency: Salem
TVK : 120 votes (45.28%)
AIADMK : 90 votes (33.96%)
DMK : 35 votes (13.21%)
BJP : 20 votes (7.55%)

🏆 Winner: TVK with 120 votes
```

---

## 🔍 Important Syntax Explained

### ✅ Sorting results by highest votes
```python
sorted_results = sorted(cons_votes.items(), key=lambda x: x[1], reverse=True)
```

Explanation:
- `cons_votes.items()` gives list of tuples: `("DMK", 120)`
- `lambda x: x[1]` sorts based on **2nd value** (votes)
- `reverse=True` sorts from **highest to lowest**

---

### ✅ Percentage formatting to 2 decimals
```python
print(f"{percent:.2f}%")
```

Explanation:
- `:.2f` prints float with **2 decimal points**
- Example: `34.56789 → 34.57`

---

## 📝 Why this project is good for learning

This project uses **simple real-world logic**, which makes it perfect for learning:

- storing records using **dictionaries + tuples**
- preventing duplicates using **sets**
- building a **menu-driven program**
- using **file handling** to store and retrieve data
- using **functions** to keep code reusable and clean

---

---

## 👩‍💻 Author

Created by **Janani** while learning Python fundamentals.

---
