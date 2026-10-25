import argparse
from service.retrieval import seed, close_qdrant

def main():
    p = argparse.ArgumentParser(description="Local vector RAG tools")
    p.add_argument("action", choices=["seed"])
    args = p.parse_args()
    if args.action == "seed":
        try:
            print(seed())
        finally:
            close_qdrant()

if __name__ == "__main__":
    main()
