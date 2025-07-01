from typing import List, NamedTuple
from kubernetes import client, config
from app.utils.logger import logger

class PodInfo(NamedTuple):
    name: str
    ns: str
    status: str

def load_kube_config(local: bool = True):
    if local:
        config.load_config()
        logger.info("Usando kubeconfig local")
    else:
        config.load_incluster_config()
        logger.info("Usando kubeconfig do cluster")

def get_pods(namespace: str) -> List[PodInfo]:
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace=namespace, watch=False)

    pod_list = [
        PodInfo(
            name=pod.metadata.labels.get("app", "sem-label"),
            ns=pod.metadata.namespace,
            status=pod.status.phase
        )
        for pod in pods.items
    ]

    logger.info(f"{len(pod_list)} pods encontrados no namespace {namespace}")
    return pod_list
