# kubernetes-sigterm-handler
handle sigterm by kubernetes

When using HPA (horizontal pod autoscaler) Kubernetes will scale down pods by sending a SIGTERM to containers within pods.
If your containers are running important applications and have connections to database / messaging queue, It is always useful to handle the SIGTERM gracefully.

This simple example shows how to handle SIGTERM using python & can be demoed on Kubernetes.

## Example

Run the deployment to create 2 pods. When you scale down replicas from 2 to 1. We can see the pod which received SIGTERM first handles it before exiting the container


![example](https://github.com/srinivasrk/kubernetes-sigterm-handler/blob/master/k8-sigterm-handler.PNG)
