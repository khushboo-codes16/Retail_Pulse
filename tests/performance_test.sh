#!/bin/bash

# Performance testing script
# Requires: hey (https://github.com/rakyll/hey)

echo "🚀 Starting RetailPulse performance tests..."

BASE_URL=${1:-"http://localhost:8000"}
REQUESTS=${2:-10000}
CONCURRENCY=${3:-100}

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2 passed${NC}"
    else
        echo -e "${RED}✗ $2 failed${NC}"
    fi
}

# Test 1: Health check
echo -e "\n${YELLOW}Test 1: Health Check${NC}"
hey -n 100 -c 10 $BASE_URL/health

# Test 2: Dashboard metrics endpoint
echo -e "\n${YELLOW}Test 2: Dashboard Metrics Endpoint${NC}"
hey -n $REQUESTS -c $CONCURRENCY $BASE_URL/api/metrics/dashboard

# Test 3: Forecast endpoint
echo -e "\n${YELLOW}Test 3: Forecast Endpoint${NC}"
hey -n $REQUESTS -c $CONCURRENCY $BASE_URL/api/forecast/30days

# Test 4: Customer segments endpoint
echo -e "\n${YELLOW}Test 4: Customer Segments Endpoint${NC}"
hey -n $REQUESTS -c $CONCURRENCY $BASE_URL/api/customers/segments

# Test 5: Mixed workload
echo -e "\n${YELLOW}Test 5: Mixed Workload${NC}"
cat > /tmp/urls.txt << EOF
$BASE_URL/api/metrics/dashboard
$BASE_URL/api/forecast/30days
$BASE_URL/api/customers/segments
$BASE_URL/api/inventory/recommendations
EOF

hey -n $REQUESTS -c $CONCURRENCY -m GET -T "application/json" -z 60s $BASE_URL/api/metrics/dashboard

echo -e "\n${GREEN}Performance testing completed!${NC}"