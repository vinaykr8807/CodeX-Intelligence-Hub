import requests
import os
from pathlib import Path

class GitHubRepoAnalyzer:
    """Analyzes GitHub repository structure and files"""
    
    def __init__(self, repo_url):
        # Parse repo URL: https://github.com/vinaykr8807/Code-snippet-recommender
        parts = repo_url.rstrip('/').split('/')
        self.owner = parts[-2]
        self.repo = parts[-1]
        self.api_base = f"https://api.github.com/repos/{self.owner}/{self.repo}"
    
    def get_repo_structure(self, path=""):
        """Get repository file tree"""
        url = f"{self.api_base}/contents/{path}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return []
        
        return response.json()
    
    def get_file_content(self, file_path):
        """Get content of a specific file"""
        url = f"{self.api_base}/contents/{file_path}"
        response = requests.get(url)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        if data.get('encoding') == 'base64':
            import base64
            return base64.b64decode(data['content']).decode('utf-8', errors='ignore')
        return None
    
    def analyze_structure(self, path="", level=0):
        """Recursively analyze repository structure"""
        items = self.get_repo_structure(path)
        structure = []
        
        for item in items:
            indent = "  " * level
            item_info = {
                "name": item['name'],
                "type": item['type'],
                "path": item['path'],
                "size": item.get('size', 0),
                "level": level
            }
            
            print(f"{indent}{'📁' if item['type'] == 'dir' else '📄'} {item['name']}")
            structure.append(item_info)
            
            # Recursively analyze directories
            if item['type'] == 'dir':
                sub_structure = self.analyze_structure(item['path'], level + 1)
                structure.extend(sub_structure)
        
        return structure
    
    def get_key_files(self):
        """Identify key files in repository"""
        key_patterns = [
            'README.md', 'requirements.txt', 'setup.py', 'package.json',
            'Dockerfile', '.env.example', 'config.py', 'main.py', 'app.py',
            '__init__.py', 'server.py', 'api.py'
        ]
        
        structure = self.analyze_structure()
        key_files = []
        
        for item in structure:
            if item['type'] == 'file':
                if any(pattern in item['name'] for pattern in key_patterns):
                    key_files.append(item)
        
        return key_files
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("="*70)
        print(f"📊 ANALYZING: {self.owner}/{self.repo}")
        print("="*70)
        
        # Get structure
        print("\n📁 Repository Structure:")
        structure = self.analyze_structure()
        
        # Statistics
        files = [i for i in structure if i['type'] == 'file']
        dirs = [i for i in structure if i['type'] == 'dir']
        
        print(f"\n📈 Statistics:")
        print(f"  Total Files: {len(files)}")
        print(f"  Total Directories: {len(dirs)}")
        print(f"  Total Size: {sum(f['size'] for f in files):,} bytes")
        
        # File types
        extensions = {}
        for f in files:
            ext = Path(f['name']).suffix or 'no_extension'
            extensions[ext] = extensions.get(ext, 0) + 1
        
        print(f"\n📝 File Types:")
        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
            print(f"  {ext}: {count}")
        
        # Key files
        print(f"\n🔑 Key Files:")
        key_files = self.get_key_files()
        for kf in key_files:
            print(f"  • {kf['path']}")
        
        return {
            "structure": structure,
            "stats": {
                "files": len(files),
                "directories": len(dirs),
                "total_size": sum(f['size'] for f in files)
            },
            "file_types": extensions,
            "key_files": key_files
        }
    
    def analyze_code_quality(self):
        """Analyze code for potential issues"""
        print("\n🔍 Code Quality Analysis:")
        
        python_files = []
        structure = self.analyze_structure()
        
        for item in structure:
            if item['type'] == 'file' and item['name'].endswith('.py'):
                python_files.append(item['path'])
        
        issues = []
        for py_file in python_files[:5]:  # Analyze first 5 Python files
            content = self.get_file_content(py_file)
            if content:
                # Simple checks
                if 'TODO' in content:
                    issues.append(f"TODO found in {py_file}")
                if 'FIXME' in content:
                    issues.append(f"FIXME found in {py_file}")
                if 'import *' in content:
                    issues.append(f"Wildcard import in {py_file}")
        
        for issue in issues:
            print(f"  ⚠️ {issue}")
        
        return issues

# Usage
if __name__ == "__main__":
    analyzer = GitHubRepoAnalyzer("https://github.com/vinaykr8807/Code-snippet-recommender")
    report = analyzer.generate_report()
    analyzer.analyze_code_quality()
