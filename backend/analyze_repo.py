from repo_analyzer import GitHubRepoAnalyzer
import json
import time

print("="*70)
print("🔍 GITHUB REPOSITORY DEEP ANALYSIS")
print("   Code-snippet-recommender by vinaykr8807")
print("="*70)

# Initialize analyzer
repo_url = "https://github.com/vinaykr8807/Code-snippet-recommender"
analyzer = GitHubRepoAnalyzer(repo_url)

# Generate full report
print("\n📊 Generating comprehensive report...")
time.sleep(1)
report = analyzer.generate_report()

# Code quality analysis
print("\n🔍 Running code quality checks...")
time.sleep(1)
issues = analyzer.analyze_code_quality()

# Additional insights
print("\n💡 Project Insights:")
print(f"  • Primary Language: Python")
print(f"  • Project Type: Code Recommendation System")
print(f"  • Total Components: {report['stats']['files']} files")

# Save detailed report
output_file = "repo_analysis_report.json"
report_data = {
    "repository": repo_url,
    "owner": "vinaykr8807",
    "repo_name": "Code-snippet-recommender",
    "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "structure": report["structure"],
    "statistics": report["stats"],
    "file_types": report["file_types"],
    "key_files": [kf["path"] for kf in report["key_files"]],
    "code_issues": issues,
    "insights": {
        "primary_language": "Python",
        "project_type": "Code Recommendation System",
        "complexity": "Medium" if report['stats']['files'] < 50 else "High"
    }
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(report_data, f, indent=2)

print(f"\n✅ Detailed report saved to: {output_file}")

# Summary
print("\n" + "="*70)
print("📋 ANALYSIS SUMMARY")
print("="*70)
print(f"Repository: {repo_url}")
print(f"Total Files: {report['stats']['files']}")
print(f"Total Directories: {report['stats']['directories']}")
print(f"Total Size: {report['stats']['total_size']:,} bytes")
print(f"Code Issues Found: {len(issues)}")
print(f"Key Files Identified: {len(report['key_files'])}")
print("="*70)

# Recommendations
print("\n🎯 Recommendations:")
if len(issues) > 0:
    print("  • Address code quality issues found")
if report['stats']['files'] > 100:
    print("  • Consider modularizing large codebase")
print("  • Ensure all dependencies are documented")
print("  • Add comprehensive README if missing")

print("\n✅ Analysis Complete!")
