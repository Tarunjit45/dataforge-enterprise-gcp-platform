# Chaos Engineering & Resiliency Testing Guide

This guide describes controlled fault injection scenarios and resiliency verification implemented in `ChaosTestingEngine`.

---

## ⚡ 1. Chaos Scenarios & Expected Recovery Behavior

| Experiment Scenario | Injected Fault | Expected Recovery Behavior | Target Max Recovery Time |
| --- | --- | --- | --- |
| **Dataproc Node Failure** | Terminate active worker node | Dataproc dynamic shuffle & task retry | 60.0 seconds |
| **BigQuery API Throttling** | Inject HTTP 429 rate limit | Exponential backoff retry decorator | 30.0 seconds |
| **AlloyDB Master Failover** | Trigger primary node failover | Client driver reconnect to read pool | 45.0 seconds |
| **Network Latency / Loss** | Drop cross-subnet packets | Socket retry and TCP retransmission | 15.0 seconds |
| **GCS Bucket Access Revocation** | Revoke bucket IAM binding | Circuit breaker isolation & quarantine logging | 10.0 seconds |
