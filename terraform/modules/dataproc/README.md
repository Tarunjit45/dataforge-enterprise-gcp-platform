# Dataproc Ephemeral Cluster Terraform Module

Provisions an ephemeral PySpark Dataproc Workflow Template with secondary Spot worker node autoscaling, private network interfaces, Stackdriver logging, and automatic cluster termination upon batch job completion.

## Features
* **Ephemeral Lifecycle**: Cluster provisions dynamically upon workflow trigger and terminates automatically upon job completion.
* **Cost Optimization**: Secondary worker nodes utilize preemptible/Spot VM compute.
* **Security**: Enforces internal IP interfaces (`internal_ip_only = true`) without public IPs.
