#!/bin/bash

# Performance test script for CV-Match Docker optimization verification

echo "=== CV-Match Performance Test ==="
echo "Starting performance tests at $(date)"
echo

# Function to test backend performance
test_backend() {
    echo "Testing backend performance..."
    for i in {1..20}; do
        curl -s -w "Time: %{time_total}s, Status: %{http_code}\n" -o /dev/null http://localhost:8000/ &
    done
    wait
    echo "Backend test completed"
    echo
}

# Function to test frontend performance  
test_frontend() {
    echo "Testing frontend performance..."
    for i in {1..20}; do
        curl -s -w "Time: %{time_total}s, Status: %{http_code}\n" -o /dev/null http://localhost:3000/ &
    done
    wait
    echo "Frontend test completed"
    echo
}

# Function to run concurrent load test
run_load_test() {
    echo "Running concurrent load test..."
    echo "Simulating 50 concurrent requests for 30 seconds..."
    
    # Backend load test
    for i in {1..10}; do
        (
            for j in {1..5}; do
                curl -s -o /dev/null http://localhost:8000/ &
                sleep 0.1
            done
            wait
        ) &
    done
    
    # Frontend load test  
    for i in {1..10}; do
        (
            for j in {1..5}; do
                curl -s -o /dev/null http://localhost:3000/ &
                sleep 0.1
            done
            wait
        ) &
    done
    
    wait
    echo "Load test completed"
    echo
}

# Get baseline metrics
echo "=== Baseline Metrics ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo

# Run tests
test_backend
test_frontend
run_load_test

# Get metrics during load
echo "=== Metrics During Load ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo

# Wait and get recovery metrics
echo "Waiting 30 seconds for recovery..."
sleep 30

echo "=== Recovery Metrics ==="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo

echo "Performance tests completed at $(date)"