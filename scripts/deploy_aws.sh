#!/bin/bash

# RetailPulse AWS Deployment Script
# Prerequisites: AWS CLI configured, kubectl installed

set -e

echo "🚀 Starting RetailPulse deployment to AWS..."

# Variables
CLUSTER_NAME="retailpulse-cluster"
REGION="us-east-1"
ECR_REPO="retailpulse"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print colored output
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Step 1: Create ECR repositories
print_message "Creating ECR repositories..."
aws ecr create-repository --repository-name $ECR_REPO-api --region $REGION || true
aws ecr create-repository --repository-name $ECR_REPO-dashboard --region $REGION || true

# Step 2: Build and push Docker images
print_message "Building and pushing Docker images..."

# Get ECR login token
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com

# Build API image
docker build -f docker/Dockerfile.api -t $ECR_REPO-api:latest .
docker tag $ECR_REPO-api:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$ECR_REPO-api:latest
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$ECR_REPO-api:latest

# Build Dashboard image
docker build -f docker/Dockerfile.dashboard -t $ECR_REPO-dashboard:latest .
docker tag $ECR_REPO-dashboard:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$ECR_REPO-dashboard:latest
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$REGION.amazonaws.com/$ECR_REPO-dashboard:latest

print_message "Docker images pushed successfully!"

# Step 3: Create EKS Cluster
print_message "Creating EKS cluster (this may take 10-15 minutes)..."

eksctl create cluster \
    --name $CLUSTER_NAME \
    --region $REGION \
    --nodegroup-name standard-workers \
    --node-type t3.medium \
    --nodes 2 \
    --nodes-min 1 \
    --nodes-max 4 \
    --managed

print_message "EKS cluster created successfully!"

# Step 4: Update kubeconfig
print_message "Updating kubeconfig..."
aws eks update-kubeconfig --region $REGION --name $CLUSTER_NAME

# Step 5: Deploy to EKS
print_message "Deploying to EKS..."
kubectl apply -f k8s/deployment.yaml

# Step 6: Create RDS PostgreSQL instance
print_message "Creating RDS PostgreSQL instance..."

aws rds create-db-instance \
    --db-instance-identifier retailpulse-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --engine-version 15.3 \
    --master-username retailpulse \
    --master-user-password SecurePassword123 \
    --allocated-storage 20 \
    --publicly-accessible false \
    --backup-retention-period 7

print_message "RDS instance creation initiated (takes ~10 minutes)"

# Step 7: Create ElastiCache Redis
print_message "Creating ElastiCache Redis cluster..."

aws elasticache create-cache-cluster \
    --cache-cluster-id retailpulse-redis \
    --cache-node-type cache.t3.micro \
    --engine redis \
    --num-cache-nodes 1

print_message "Redis cluster creation initiated"

# Step 8: Create S3 bucket for model storage
print_message "Creating S3 bucket for models..."
S3_BUCKET="retailpulse-models-$(aws sts get-caller-identity --query Account --output text)"
aws s3 mb s3://$S3_BUCKET --region $REGION
aws s3api put-bucket-versioning --bucket $S3_BUCKET --versioning-configuration Status=Enabled

# Step 9: Get service endpoints
print_message "Getting service endpoints..."
sleep 30
API_URL=$(kubectl get svc api-service -n retailpulse -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
DASHBOARD_URL=$(kubectl get svc dashboard-service -n retailpulse -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

print_message "Deployment complete!"
echo ""
echo "=========================================="
echo "✅ RetailPulse Deployment Summary"
echo "=========================================="
echo "API URL: http://$API_URL"
echo "Dashboard URL: http://$DASHBOARD_URL"
echo "MLflow UI: http://$API_URL/mlflow"
echo ""
echo "S3 Bucket: s3://$S3_BUCKET"
echo "RDS Endpoint: retailpulse-db.xxxxx.rds.amazonaws.com"
echo "Redis Endpoint: retailpulse-redis.xxxxx.cache.amazonaws.com"
echo "=========================================="

# Step 10: Set up CloudWatch monitoring
print_message "Setting up CloudWatch monitoring..."

aws cloudwatch put-dashboard \
    --dashboard-name RetailPulse \
    --dashboard-body file://scripts/cloudwatch-dashboard.json

print_message "CloudWatch dashboard created!"

# Step 11: Deploy CloudFront CDN
print_message "Deploying CloudFront CDN for dashboard..."

aws cloudfront create-distribution \
    --origin-domain-name $DASHBOARD_URL \
    --default-root-object index.html \
    --enabled

print_message "CloudFront CDN deployed!"

echo ""
print_message "🎉 Deployment completed successfully!"