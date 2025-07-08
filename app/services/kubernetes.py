from typing import List, NamedTuple, Any, Optional
from kubernetes import client, config
from kubernetes.client import ApiException
from app.utils.logger import logger

class PodInfo(NamedTuple):
    name: str
    ns: str
    status: Optional[str] = None

def load_kube_config(local: bool = True):
    if local:
        config.load_config()
        logger.info("Usando kubeconfig local")
    else:
        config.load_incluster_config()
        logger.info("Usando kubeconfig do cluster")

def get_pods(namespace: str, label: Optional[str] = None) -> Any:
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace=namespace, label_selector=label, watch=False)

    pod_list = [
        PodInfo(
            name=pod.metadata.name,
            ns=pod.metadata.namespace,
            status=pod.status.phase
        ) for pod in pods.items
    ]

    logger.info(f"{len(pod_list)} pods encontrados em {namespace}")
    return pod_list

def delete_pods(namespace: str, pod_name: str):
    v1 = client.CoreV1Api()

    try:
        v1.delete_namespaced_pod(namespace=namespace, name=pod_name)
        logger.info(f"Deletando pod {pod_name}.")
    except ApiException as e:
        logger.error(f"Falha ao deletar {namespace}/{pod_name}: {e.reason}")

def pod_logs(namespace: str, pod_name: str) -> Any:
    v1 = client.CoreV1Api()

    try:
        logs = v1.read_namespaced_pod_log(namespace=namespace, name=pod_name, tail_lines=300)
        logger.info(f"Retornando log de {pod_name}")

        return logs

    except ApiException as e:
        logger.error(f"Falha ao recuperar log do {pod_name}: {e.body}")

        return None
