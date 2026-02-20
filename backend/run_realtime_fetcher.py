from realtime_fetcher import RealTimeBugFetcher
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
LANGUAGES = ["python", "javascript", "java", "cpp", "go", "rust", "typescript"]
TAGS = ["python", "javascript", "reactjs", "nodejs", "docker", "kubernetes", "aws"]

# Get paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_dir = os.path.join(base_dir, "Model")

print("="*70)
print("🚀 REAL-TIME BUG FETCHER")
print("="*70)

# Initialize fetcher
fetcher = RealTimeBugFetcher(
    model_dir=model_dir,
    stack_key=os.getenv("STACK_KEY", "rl_DSbgxpSWTj1gMdjhYHsxjLrWQ")
)

# Choose mode
print("\nSelect mode:")
print("1. Run once (fetch and update)")
print("2. Run continuously (every 60 minutes)")
print("3. Custom interval")

choice = input("\nEnter choice (1/2/3): ").strip()

if choice == "1":
    fetcher.run_once(LANGUAGES, TAGS)
elif choice == "2":
    fetcher.run_continuous(LANGUAGES, TAGS, interval_minutes=60)
elif choice == "3":
    interval = int(input("Enter interval in minutes: "))
    fetcher.run_continuous(LANGUAGES, TAGS, interval_minutes=interval)
else:
    print("❌ Invalid choice")
