# CV-Match Docker Monitoring Stack

This monitoring stack provides comprehensive monitoring for the CV-Match Docker containers, including CPU usage, memory usage, network I/O, disk I/O, and container health status.

## Architecture

The monitoring stack consists of the following components:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **cAdvisor**: Container resource usage metrics
- **Node Exporter**: System-level metrics
- **Alertmanager**: Alert routing and notifications

## Quick Start

To start the monitoring stack:

```bash
# Start the main application first
docker-compose up -d

# Then start the monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d
```

## Access Points

Once the monitoring stack is running, you can access the following services:

- **Grafana Dashboard**: http://localhost:3001
  - Username: admin
  - Password: admin123

- **Prometheus**: http://localhost:9090

- **cAdvisor**: http://localhost:8080

- **Node Exporter**: http://localhost:9100

- **Alertmanager**: http://localhost:9093

## Monitoring Features

### Container Metrics

- **CPU Usage**: Real-time CPU usage per container
- **Memory Usage**: Memory consumption and limits
- **Network I/O**: Network traffic per container
- **Disk I/O**: Disk read/write operations
- **Container Health**: Health check status and restarts

### System Metrics

- **Host CPU**: Overall system CPU usage
- **Host Memory**: System memory consumption
- **Host Disk**: Disk space usage
- **Network**: System network statistics

### Application Metrics

- **Frontend**: Next.js application metrics
- **Backend**: FastAPI application metrics
- **Response Times**: Application performance metrics
- **Error Rates**: Application error tracking

## Alerting

The monitoring stack includes comprehensive alerting for:

### Container Alerts

- High CPU usage (>80% warning, >95% critical)
- High memory usage (>85% warning, >95% critical)
- Container restarts
- Health check failures
- High disk I/O
- High network I/O

### System Alerts

- Host high CPU usage
- Host high memory usage
- Low disk space

### Application Alerts

- Service downtime
- High response times
- High error rates

### Monitoring Alerts

- Monitoring service failures
- Target scraping failures

## Configuration

### Prometheus Configuration

The Prometheus configuration is located at `monitoring/prometheus/prometheus.yml` and includes:

- Scrape configurations for all services
- Alert rules loading
- Alertmanager configuration

### Alert Rules

Alert rules are defined in `monitoring/prometheus/alert_rules.yml` and include:

- Container resource usage alerts
- System resource alerts
- Application performance alerts
- Monitoring system alerts

### Grafana Dashboards

The main dashboard is automatically provisioned from `monitoring/grafana/dashboards/docker-metrics.json` and includes:

- Container CPU and memory usage
- Network and disk I/O
- System resource overview
- Application-specific metrics

## Resource Limits

The monitoring stack is configured with resource limits to minimize its own CPU usage:

- **Prometheus**: 0.5 CPU limit, 512MB memory limit
- **Grafana**: 0.25 CPU limit, 256MB memory limit
- **cAdvisor**: 0.25 CPU limit, 128MB memory limit
- **Node Exporter**: 0.125 CPU limit, 64MB memory limit
- **Alertmanager**: 0.25 CPU limit, 128MB memory limit

## Data Retention

- **Prometheus**: 200 hours of metrics retention
- **Grafana**: Persistent dashboard and user data storage

## Security Considerations

- All services run with non-root users where applicable
- Grafana is configured with a secure admin password
- Network isolation between monitoring and application services
- No sensitive data is stored in container images

## Troubleshooting

### Check Service Status

```bash
docker-compose -f docker-compose.monitoring.yml ps
```

### View Logs

```bash
# View all logs
docker-compose -f docker-compose.monitoring.yml logs

# View specific service logs
docker-compose -f docker-compose.monitoring.yml logs prometheus
docker-compose -f docker-compose.monitoring.yml logs grafana
```

### Check Health Status

```bash
# Check Prometheus health
curl http://localhost:9090/-/healthy

# Check Grafana health
curl http://localhost:3001/api/health

# Check cAdvisor health
curl http://localhost:8080/healthz
```

### Reload Prometheus Configuration

```bash
# Reload Prometheus without restarting
curl -X POST http://localhost:9090/-/reload
```

## Customization

### Adding New Metrics

1. Update `monitoring/prometheus/prometheus.yml` with new scrape targets
2. Add alert rules to `monitoring/prometheus/alert_rules.yml`
3. Create new Grafana dashboards or update existing ones

### Modifying Alert Rules

Edit `monitoring/prometheus/alert_rules.yml` and reload Prometheus:

```bash
curl -X POST http://localhost:9090/-/reload
```

### Updating Grafana Dashboards

1. Modify dashboard JSON files in `monitoring/grafana/dashboards/`
2. Restart Grafana: `docker-compose -f docker-compose.monitoring.yml restart grafana`

## Integration with CI/CD

The monitoring stack can be integrated into CI/CD pipelines:

```bash
# Validate configuration
docker-compose -f docker-compose.monitoring.yml config

# Test monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d
sleep 30
curl -f http://localhost:9090/-/healthy
curl -f http://localhost:3001/api/health
docker-compose -f docker-compose.monitoring.yml down
```

## Performance Optimization

The monitoring stack is optimized for minimal resource usage:

- Efficient scrape intervals (15s for most metrics)
- Optimized Prometheus storage configuration
- Lightweight container images
- Resource limits to prevent monitoring overhead

## Backup and Recovery

### Backup Data

```bash
# Backup Prometheus data
docker run --rm -v cv-match_prometheus_data:/data -v $(pwd):/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /data .

# Backup Grafana data
docker run --rm -v cv-match_grafana_data:/data -v $(pwd):/backup alpine tar czf /backup/grafana-backup.tar.gz -C /data .
```

### Restore Data

```bash
# Restore Prometheus data
docker run --rm -v cv-match_prometheus_data:/data -v $(pwd):/backup alpine tar xzf /backup/prometheus-backup.tar.gz -C /data

# Restore Grafana data
docker run --rm -v cv-match_grafana_data:/data -v $(pwd):/backup alpine tar xzf /backup/grafana-backup.tar.gz -C /data
```

## Maintenance

### Regular Tasks

- Review alert rules and thresholds
- Update container images for security patches
- Monitor monitoring system performance
- Archive old metrics data if needed

### Cleanup

```bash
# Remove old containers and images
docker system prune -f

# Remove unused volumes (be careful!)
docker volume prune -f