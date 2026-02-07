from src.sessions.run_session import run_session

def main():
    print("\nWelcome to the cognitive test demo.")
    print("This is NOT a diagnosis. Just a learning tool.\n")

    participant_id = input("Enter your participant ID (e.g. 'me'): ")

    print("\nStarting session...\n")
    results = run_session(participant_id)

    print("\n=== SESSION COMPLETE ===\n")

    for task_name, result in results.items():
        print(f"{task_name.upper()}")
        print(f"  Score: {result['score']}")
        if "metrics" in result:
            for k, v in result["metrics"].items():
                print(f"  {k}: {v}")
        print()

if __name__ == "__main__":
    main()
