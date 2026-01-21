# ==========================================
# Tamil Nadu Election Simulator (Console App)
# Covers: operators, datatypes, list, set,
# tuple, dict, control flow, nested if, loops,
# functions, error handling, file handling, imports
# ==========================================

import random
from datetime import datetime

VOTERS_FILE = "voters.txt"
VOTES_FILE = "votes.txt"

# Constituencies sample
CONSTITUENCIES = ["Chennai Central", "Madurai", "Coimbatore", "Tirunelveli", "Salem"]


# -----------------------------
# File Handling Functions
# -----------------------------
def load_voters():
    voters = {}  # dict: voter_id -> tuple(name, age, constituency)
    try:
        with open(VOTERS_FILE, "r") as f:
            for line in f:
                voter_id, name, age, cons = line.strip().split(",")
                voters[voter_id] = (name, int(age), cons)
    except FileNotFoundError:
        pass
    return voters


def save_voters(voters):
    try:
        with open(VOTERS_FILE, "w") as f:
            for voter_id, details in voters.items():
                name, age, cons = details
                f.write(f"{voter_id},{name},{age},{cons}\n")
    except Exception as e:
        print("❌ Error saving voters:", e)


def load_votes():
    votes = {}  # dict: constituency -> dict(candidate -> votes)
    voted_voters = set()  # set of voter_ids who voted already

    try:
        with open(VOTES_FILE, "r") as f:
            for line in f:
                voter_id, cons, candidate = line.strip().split(",")
                voted_voters.add(voter_id)

                if cons not in votes:
                    votes[cons] = {}

                votes[cons][candidate] = votes[cons].get(candidate, 0) + 1

    except FileNotFoundError:
        pass

    return votes, voted_voters


def save_vote(voter_id, constituency, candidate):
    try:
        with open(VOTES_FILE, "a") as f:
            f.write(f"{voter_id},{constituency},{candidate}\n")
    except Exception as e:
        print("❌ Error saving vote:", e)


# -----------------------------
# Utility Functions
# -----------------------------
def generate_voter_id(name):
    # importing datetime used here
    now = datetime.now().strftime("%H%M%S")
    # operator usage + string
    return f"TN{name[:2].upper()}{random.randint(100, 999)}{now}"


def show_constituencies():
    print("\n📍 Available Constituencies:")
    for i, c in enumerate(CONSTITUENCIES, start=1):
        print(f"{i}. {c}")


def get_constituency_choice():
    show_constituencies()
    while True:
        try:
            choice = int(input("Select constituency number: "))
            if 1 <= choice <= len(CONSTITUENCIES):
                return CONSTITUENCIES[choice - 1]
            else:
                print("❌ Invalid constituency number.")
        except ValueError:
            print("❌ Please enter a valid number.")


# -----------------------------
# Election Data
# -----------------------------
def default_candidates():
    # dict: constituency -> list of candidates
    return {
        "Chennai Central": ["TVK","DMK", "AIADMK", "BJP", "NTK"],
        "Madurai": ["TVK","DMK", "AIADMK", "BJP", "NTK"],
        "Coimbatore": ["TVK","DMK", "AIADMK", "BJP", "NTK"],
        "Tirunelveli": ["TVK","DMK", "AIADMK", "BJP", "NTK"],
        "Salem": ["TVK","DMK", "AIADMK", "BJP", "NTK"]
    }


# -----------------------------
# Core Features
# -----------------------------
def register_voter(voters):
    print("\n🧾 Voter Registration")

    name = input("Enter voter name: ").strip()

    try:
        age = int(input("Enter age: "))

        # operators + nested if
        if age >= 18:
            constituency = get_constituency_choice()
            voter_id = generate_voter_id(name)

            # tuple stored inside dict
            voters[voter_id] = (name, age, constituency)

            save_voters(voters)

            print("\n✅ Registration successful!")
            print("Your Voter ID:", voter_id)
            print("Constituency:", constituency)

        else:
            print("❌ Not eligible to vote. Minimum age is 18.")

    except ValueError:
        print("❌ Age must be a number.")


def cast_vote(voters, votes, voted_voters, candidates):
    print("\n🗳️ Cast Vote")

    voter_id = input("Enter your Voter ID: ").strip()

    # control flow
    if voter_id not in voters:
        print("❌ Voter not found. Register first.")
        return

    # set usage: prevent duplicate voting
    if voter_id in voted_voters:
        print("⚠️ You already voted. Duplicate voting not allowed.")
        return

    name, age, constituency = voters[voter_id]

    print(f"\n👤 Welcome {name} ({age})")
    print("📍 Your constituency:", constituency)

    # list usage
    candidate_list = candidates.get(constituency, [])

    if not candidate_list:
        print("❌ No candidates found for this constituency.")
        return

    print("\nCandidates:")
    for i, c in enumerate(candidate_list, start=1):
        print(f"{i}. {c}")

    while True:
        try:
            choice = int(input("Choose candidate number: "))
            if 1 <= choice <= len(candidate_list):
                selected = candidate_list[choice - 1]

                # save vote
                save_vote(voter_id, constituency, selected)

                # update runtime structures
                voted_voters.add(voter_id)
                votes.setdefault(constituency, {})
                votes[constituency][selected] = votes[constituency].get(selected, 0) + 1

                print(f"\n✅ Vote cast successfully for {selected}!")
                break
            else:
                print("❌ Invalid candidate number.")
        except ValueError:
            print("❌ Enter a valid number.")


def view_results(votes):
    print("\n📊 Election Results (Constituency-wise)")

    if not votes:
        print("⚠️ No votes cast yet.")
        return

    for cons, cons_votes in votes.items():
        print("\n========================")
        print("Constituency:", cons)
        print("========================")

        total_votes = sum(cons_votes.values())

        if total_votes == 0:
            print("No votes in this constituency.")
            continue

        # tuple and sorting
        sorted_results = sorted(cons_votes.items(), key=lambda x: x[1], reverse=True)

        for party, count in sorted_results:
            # operators
            percent = (count / total_votes) * 100
            print(f"{party} : {count} votes ({percent:.2f}%)")

        # declare winner
        winner_party, winner_votes = sorted_results[0]
        print("🏆 Winner:", winner_party, "with", winner_votes, "votes")


def state_summary(votes):
    print("\n🟦 Tamil Nadu State Summary")

    if not votes:
        print("⚠️ No votes cast yet.")
        return

    state_party_count = {}  # dict party -> total votes

    for cons, cons_votes in votes.items():
        for party, count in cons_votes.items():
            state_party_count[party] = state_party_count.get(party, 0) + count

    total_votes = sum(state_party_count.values())
    print("Total Votes Cast:", total_votes)

    # show parties set
    parties = set(state_party_count.keys())
    print("Parties Participated:", parties)

    sorted_state = sorted(state_party_count.items(), key=lambda x: x[1], reverse=True)

    print("\n--- Party Vote Share ---")
    for party, count in sorted_state:
        share = (count / total_votes) * 100 if total_votes else 0
        print(f"{party}: {count} votes ({share:.2f}%)")

    # Overall winner
    overall_winner, w_votes = sorted_state[0]
    print("\n🏆 Overall Leading Party:", overall_winner)


def reset_election():
    # file handling
    open(VOTES_FILE, "w").close()
    print("✅ Votes reset successfully (for fresh simulation).")


# -----------------------------
# Main Program
# -----------------------------
def main():
    print("===========================================")
    print("🗳️ Tamil Nadu Election Console Simulator")
    print("===========================================")
    print("📅 Date:", datetime.now().strftime("%d-%m-%Y"))

    voters = load_voters()
    votes, voted_voters = load_votes()
    candidates = default_candidates()

    while True:
        print("\n------ MENU ------")
        print("1. Register Voter")
        print("2. Cast Vote")
        print("3. View Constituency Results")
        print("4. State Summary")
        print("5. Reset Votes (Simulation)")
        print("6. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            register_voter(voters)

        elif choice == "2":
            cast_vote(voters, votes, voted_voters, candidates)

        elif choice == "3":
            view_results(votes)

        elif choice == "4":
            state_summary(votes)

        elif choice == "5":
            reset_election()
            votes.clear()
            voted_voters.clear()

        elif choice == "6":
            print("✅ Exiting. Thanks for using election simulator 👋")
            break
        else:
            print("❌ Invalid choice. Try again.")


if __name__ == "__main__":
    main()
