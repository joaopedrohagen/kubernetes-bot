from os import name
from typing import List, NamedTuple
from kubernetes import client, config
from app.utils.logger import logger

class PodInfo(NamedTuple):
    name: str
    ns: str
    status: str | None = None

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
            name=pod.metadata.labels.get("app", pod.metadata.name),
            ns=pod.metadata.namespace,
            status=pod.status.phase
        )
        for pod in pods.items
    ]

    logger.info(f"{len(pod_list)} pods encontrados no namespace {namespace}")
    return pod_list

def delete_pods(namespace: str, label: str):
    v1 = client.CoreV1Api()
    pods= v1.list_namespaced_pod(namespace=namespace, label_selector=f"app={label}", watch=False)

    pod_list = [
        PodInfo(
            name=pod.metadata.name,
            ns=pod.metadata.namespace
        ) for pod in pods.items
    ]

    print(pods)

    if not pod_list:
        logger.error(f"Nenhum pod encontrado com a label 'app={label}' no namespace {namespace}")
        return

    for pod in pod_list:
        v1.delete_namespaced_pod(namespace=pod.ns, name=pod.name)
        logger.info(f"Deletando pod: {pod.ns}/{pod.name}")

