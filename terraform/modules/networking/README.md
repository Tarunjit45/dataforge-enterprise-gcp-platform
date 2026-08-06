# Networking Terraform Module

Provisions Custom VPC, Private Subnets, Cloud Router, Cloud NAT, and internal VPC Firewall rules.

## Resources
* `google_compute_network.vpc`: Dedicated Private VPC Network.
* `google_compute_subnetwork.private_subnet`: Regional Private Subnet with Private Google Access.
* `google_compute_router.nat_router`: Cloud Router for NAT outbound connectivity.
* `google_compute_router_nat.nat`: Cloud NAT enabling internet egress for private VMs without public IPs.
* `google_compute_firewall.allow_internal`: Internal traffic allowance rule.
