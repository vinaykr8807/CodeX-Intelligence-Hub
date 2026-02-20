from realtime_fetcher import RealTimeBugFetcher
import os
from dotenv import load_dotenv
import schedule
import time

load_dotenv()

# Configuration
LANGUAGES = ["python", "javascript", "java", "cpp", "go", "rust", "typescript", "csharp"]
TAGS = ["python", "javascript", "reactjs", "nodejs", "docker", "kubernetes", "aws", "tensorflow", "pytorch"]

# Get paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_dir = os.path.join(base_dir, "Model")

print("="*70)
print("⏰ AUTOMATED BUG FETCHER SCHEDULER")
print("="*70)

# Initialize fetcher
fetcher = RealTimeBugFetcher(
    model_dir=model_dir,
    stack_key=os.getenv("STACK_KEY", "rl_DSbgxpSWTj1gMdjhYHsxjLrWQ")
)

def fetch_job():
    """Job to run on schedule"""
    print(f"\n{'='*70}")
    print(f"🔄 Running scheduled fetch...")
    print(f"{'='*70}")
    fetcher.run_once(LANGUAGES, TAGS)

# Schedule options
print("\nSchedule Options:")
print("1. Every 1 hour")
print("2. Every 6 hours")
print("3. Every 12 hours")
print("4. Daily at 2 AM")

choice = input("\nEnter choice (1/2/3/4): ").strip()

if choice == "1":
    schedule.every(1).hours.do(fetch_job)
    print("✅ Scheduled: Every 1 hour")
elif choice == "2":
    schedule.every(6).hours.do(fetch_job)
    print("✅ Scheduled: Every 6 hours")
elif choice == "3":
    schedule.every(12).hours.do(fetch_job)
    print("✅ Scheduled: Every 12 hours")
elif choice == "4":
    schedule.every().day.at("02:00").do(fetch_job)
    print("✅ Scheduled: Daily at 2 AM")
else:
    print("❌ Invalid choice")
    exit()

# Run first fetch immediately
print("\n🚀 Running initial fetch...")
fetch_job()

# Keep running
print("\n⏳ Scheduler running... (Press Ctrl+C to stop)")
while True:
    schedule.run_pending()
    time.sleep(60)
