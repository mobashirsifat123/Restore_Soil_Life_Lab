"""
Recommended metrics to emit:

- queue_messages_reserved_total{queue_name}
- queue_messages_acknowledged_total{queue_name}
- queue_messages_dead_lettered_total{queue_name}
- job_duration_seconds{job_type,status}
- job_retries_total{job_type}
- job_timeouts_total{job_type}
- worker_heartbeat_lag_seconds
- running_jobs_gauge{job_type}
- artifact_upload_duration_seconds{artifact_type}
"""
