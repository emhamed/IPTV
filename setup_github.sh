#!/bin/bash

echo "🚀 Setting up GitHub repository for IPTV playlist..."
echo "=================================================="

# Get GitHub username
echo "📝 Please enter your GitHub username:"
read -p "Username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ No username provided. Exiting."
    exit 1
fi

echo "✅ Using GitHub username: $GITHUB_USERNAME"

# Set up remote
echo "🔗 Setting up GitHub remote..."
git remote add origin https://github.com/$GITHUB_USERNAME/iptv-playlist.git

# Push to GitHub
echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "🎉 SUCCESS! Your IPTV playlist is now on GitHub!"
echo "=================================================="
echo "📺 Your playlist URL: https://$GITHUB_USERNAME.github.io/iptv-playlist/playlist.m3u"
echo ""
echo "📋 Next steps:"
echo "1. Go to: https://github.com/$GITHUB_USERNAME/iptv-playlist"
echo "2. Click 'Settings' tab"
echo "3. Scroll to 'Pages' section"
echo "4. Source: Deploy from a branch"
echo "5. Branch: main"
echo "6. Folder: / (root)"
echo "7. Click 'Save'"
echo ""
echo "🎮 For your PS5, use this URL:"
echo "https://$GITHUB_USERNAME.github.io/iptv-playlist/playlist.m3u"
echo ""
echo "✅ You can now turn off your Mac and your PS5 will still work!"
