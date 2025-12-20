#!/bin/bash
set -e

# Configuration from AWS_DEPLOYMENT_SUMMARY.md
SERVER_IP="3.219.214.103"
USER="ec2-user"
KEY="~/.ssh/voice-agent-key.pem"
REMOTE_DIR="~/voice_agent"

echo "🚀 Deploying updates to AWS ($SERVER_IP)..."

# 1. Update Code - Uploading Python scripts, text prompts, Dockerfile, and Static assets
echo "📦 Uploading files..."
scp -i $KEY *.py *.txt Dockerfile requirements.txt $USER@$SERVER_IP:$REMOTE_DIR/
scp -i $KEY -r static $USER@$SERVER_IP:$REMOTE_DIR/

# 2. Rebuild Container via SSH
echo "🔄 Rebuilding Docker container on server..."
ssh -i $KEY $USER@$SERVER_IP << EOF
    cd $REMOTE_DIR
    
    # Stop and remove existing container
    sudo docker stop jess-voice-agent || true
    sudo docker rm jess-voice-agent || true
    
    # Build new image (using updated Dockerfile which now copies *.txt and *.py)
    sudo docker build -t jess-voice-agent .
    
    # Run container
    sudo docker run -d --name jess-voice-agent \
        --restart unless-stopped \
        --env-file .env \
        -p 8000:8000 \
        -v ~/voice_agent/logs:/app/logs \
        jess-voice-agent
    
    # Cleanup
    sudo docker image prune -f
EOF

echo "✅ Deployment complete!"
echo "🌍 Testing health check..."
curl -k https://$SERVER_IP/health
echo ""
echo "Please verify the Proposal Page at: https://$SERVER_IP/static/proposal.html"
