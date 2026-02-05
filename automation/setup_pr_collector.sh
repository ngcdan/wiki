#!/bin/bash
# Setup script cho Forgejo PR Collector

echo "🔧 Setting up Forgejo PR Collector..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit forgejo_pr_collector.py and update:"
echo "   - FORGEJO_URL"
echo "   - ACCESS_TOKEN"
echo "   - OWNER"
echo "   - REPOS"
echo ""
echo "2. Run the collector:"
echo "   source venv/bin/activate"
echo "   python forgejo_pr_collector.py"
echo ""
echo "3. (Optional) Setup cron job for automatic collection:"
echo "   crontab -e"
echo "   # Add: 0 9 * * * cd /path/to/script && ./venv/bin/python forgejo_pr_collector.py"
