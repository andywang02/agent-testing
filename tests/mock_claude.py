import sys
import time

def main():
    print("Mock Claude started.")
    print(f"Arguments: {sys.argv[1:]}")

    while True:
        try:
            line = input("Claude> ")
            print(f"Received: {line}")
            if line.strip().lower() == "exit":
                break
        except EOFError:
            break
        except KeyboardInterrupt:
            break
    print("Mock Claude exiting.")

if __name__ == "__main__":
    main()
