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

# 🔍 Important Syntax Explained (Full Coverage)

This section explains the **most important syntax patterns used across the program**, so you understand *every concept*, not only a few lines.

---

## 1) Importing Modules

```python
import random
from datetime import datetime
```

- `import random` imports the full module.
- `from datetime import datetime` imports only `datetime` class.
- Used for random ID creation and time display.

---

## 2) Constants

```python
VOTERS_FILE = "voters.txt"
VOTES_FILE = "votes.txt"
```

- Variables in CAPS are treated as constants (convention).
- Used for filenames.

---

## 3) Lists

```python
CONSTITUENCIES = ["Chennai Central", "Madurai", "Coimbatore", "Tirunelveli", "Salem"]
```

- List stores multiple values in an ordered manner.
- Used for showing constituency choices.

---

## 4) Dictionaries

### Basic dictionary
```python
voters = {}
```

- Used to map `voter_id -> voter details`.

### Nested dictionary
```python
votes = {
    "Salem": {"DMK": 10, "AIADMK": 8}
}
```

- Used to map `constituency -> {party -> votes}`

---

## 5) Tuples

```python
voters[voter_id] = (name, age, constituency)
```

- Tuple stores fixed record data.
- Used for voter record since it doesn't need modification frequently.

### Tuple unpacking
```python
name, age, constituency = voters[voter_id]
```

---

## 6) Sets

```python
voted_voters = set()
```

- Stores unique voter ids.
- Used to prevent multiple votes by same voter.

### Add into set
```python
voted_voters.add(voter_id)
```

### Membership check
```python
if voter_id in voted_voters:
    print("Already voted")
```

---

## 7) Functions (`def`)

```python
def register_voter(voters):
    ...
```

- `def` defines a function.
- Helps split code into reusable blocks.

---

## 8) User Input and Type Conversion

```python
age = int(input("Enter age: "))
marks = float(input("Enter marks: "))
```

- `input()` always returns a string.
- So we convert using `int()` or `float()`.

---

## 9) Control Flow (`if/elif/else`)

```python
if age >= 18:
    ...
else:
    ...
```

### Nested if
```python
if marks >= 0 and marks <= 100:
    if marks >= 90:
        grade = "A"
    elif marks >= 75:
        grade = "B"
    else:
        grade = "C"
```

---

## 10) Loops

### for loop
```python
for i, c in enumerate(CONSTITUENCIES, start=1):
    print(i, c)
```

### while loop
```python
while True:
    choice = input("Enter choice: ")
    if choice == "6":
        break
```

---

## 11) `enumerate()` usage

```python
for i, c in enumerate(CONSTITUENCIES, start=1):
```

- Gives index + item.
- `start=1` gives human-friendly numbering.

---

## 12) File Handling

### Read file
```python
with open(VOTERS_FILE, "r") as f:
    for line in f:
        ...
```

### Write file (overwrite)
```python
with open(VOTERS_FILE, "w") as f:
    f.write(...)
```

### Append file (add at end)
```python
with open(VOTES_FILE, "a") as f:
    f.write(...)
```

✅ `with open(...)` closes file automatically.

---

## 13) String Operations

### Strip newline
```python
line.strip()
```

### Split CSV fields
```python
line.strip().split(",")
```

### Join inside f-string
```python
f"{voter_id},{name},{age},{cons}\n"
```

---

## 14) Exception Handling (`try/except`)

```python
try:
    age = int(input("Enter age: "))
except ValueError:
    print("Invalid input")
```

### File not found handling
```python
except FileNotFoundError:
    pass
```

---

## 15) `dict.get()` method

```python
count = votes.get(party, 0)
```

- Prevents KeyError.
- Returns default value if key not found.

Used in:
```python
votes[cons][candidate] = votes[cons].get(candidate, 0) + 1
```

---

## 16) `dict.setdefault()` method

```python
votes.setdefault(constituency, {})
```

- If key doesn't exist → creates it with empty dict.

---

## 17) Sorting Results (VERY IMPORTANT)

```python
sorted_results = sorted(cons_votes.items(), key=lambda x: x[1], reverse=True)
```

- `.items()` returns list of tuples: `(party, votes)`
- `lambda x: x[1]` means sort by votes (2nd element)
- `reverse=True` makes highest first

---

## 18) Lambda Function

```python
lambda x: x[1]
```

Meaning:
- anonymous function
- takes `x` (tuple like `("DMK",120)`)
- returns `x[1]` (votes)

Equivalent:
```python
def get_votes(x):
    return x[1]
```

---

## 19) Calculations and Operators

### Total votes
```python
total_votes = sum(cons_votes.values())
```

### Percentage
```python
percent = (count / total_votes) * 100
```

---

## 20) f-string Formatting

### Insert variables
```python
print(f"Voter ID: {voter_id}")
```

### 2 decimal places
```python
print(f"{percent:.2f}%")
```

- `.2f` prints 2 digits after decimal.

---

## 21) Reset votes file

```python
open(VOTES_FILE, "w").close()
```

- Opens in write mode → clears contents
- Closes immediately

---

## 22) Program Entry Point

```python
if __name__ == "__main__":
    main()
```

Meaning:
- Run only when this file is executed directly.
- Prevents auto execution when imported.

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
