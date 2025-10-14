#!/bin/bash

# Deploy Hide4 Control Dashboard to Firebase Hosting
# This script will deploy the webapp to Firebase Hosting

echo "🚀 Deploying Hide4 Control Dashboard to Firebase Hosting..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Check if user is logged in
if ! firebase projects:list &> /dev/null; then
    echo "❌ Not logged in to Firebase. Please run: firebase login"
    exit 1
fi

# Initialize Firebase project if not already done
if [ ! -f ".firebaserc" ]; then
    echo "📝 Initializing Firebase project..."
    firebase init hosting --project hide4-control-dashboard
fi

# Build the webapp (if needed)
echo "🔨 Building webapp..."
cd webapp

# Create a simple build script
cat > build.sh << 'EOF'
#!/bin/bash
echo "Building Hide4 Control Dashboard..."

# Copy all files to dist directory
mkdir -p dist
cp -r * dist/

# Update Firebase config with actual values (placeholder)
echo "⚠️  Remember to update Firebase config in js/firebase-config.js with actual values!"

echo "✅ Build completed!"
EOF

chmod +x build.sh
./build.sh

cd ..

# Deploy to Firebase Hosting
echo "🌐 Deploying to Firebase Hosting..."
firebase deploy --only hosting

echo "✅ Deployment completed!"
echo "🌐 Your dashboard is now available at: https://hide4-control-dashboard.web.app"
echo ""
echo "📋 Next steps:"
echo "1. Update Firebase config in webapp/js/firebase-config.js with actual values"
echo "2. Update config.json.example with your Firebase credentials"
echo "3. Test the dashboard by visiting the URL above"
echo "4. Install Hide4.exe on machines and configure with Firebase credentials"
