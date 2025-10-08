#!/bin/bash

echo "=== Crawler Status ==="
echo "Time: $(date)"
echo

# Check if crawler is running
if pgrep -f "crawl_by_metadata.py" > /dev/null; then
    PID=$(pgrep -f "crawl_by_metadata.py")
    echo "✅ Crawler is running"
    echo "PID: $PID"
else
    echo "❌ Crawler is not running"
fi

echo

# CPU Temperature (macOS)
if command -v osx-cpu-temp &> /dev/null; then
    echo "🌡️  CPU Temperature: $(osx-cpu-temp)"
else
    echo "🌡️  CPU Temperature: Not available (install osx-cpu-temp)"
fi

# Memory usage
echo "💾 Memory usage:"
ps aux | grep python | grep -v grep | head -5

echo

# Latest progress from log
if [ -f "crawler.log" ]; then
    echo "📈 Latest progress:"
    grep "Updated progress:" crawler.log | tail -1
    echo
fi

# Log tail
echo "📝 Log tail:"
if [ -f "crawler.log" ]; then
    tail -5 crawler.log
else
    echo "No crawler.log found"
fi