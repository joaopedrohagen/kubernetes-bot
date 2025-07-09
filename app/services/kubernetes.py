from typing import NamedTuple, Any, Optional
from kubernetes import client, config
from kubernetes.client import ApiException
from app.utils.logger import logger
from base64 import b64decode

class KubeResourceInfo(NamedTuple):
    name: str
    ns: str
    status: Optional[str] = None
    data: Optional[dict[str, str]] = None

class KubernetesClient:
  def __init__(self, local: bool = True):
    if local:
      config.load_config()
      logger.info("Usando kubeconfig local")
    else:
      config.load_incluster_config()
      logger.info("Usando kubeconfig do cluster")

    self.v1 = client.CoreV1Api()

  def get_pods(self, namespace: str, label: Optional[str] = None) -> Any:
    pods = self.v1.list_namespaced_pod(namespace=namespace, label_selector=label, watch=False)

    pod_list = [
        KubeResourceInfo(
            name=pod.metadata.name,
            ns=pod.metadata.namespace,
            status=pod.status.phase
        ) for pod in pods.items
    ]

    logger.info(f"{len(pod_list)} pods encontrados em {namespace}")
    return pod_list

  def get_secrets(self, namespace: str) -> Any:
      secrets = self.v1.list_namespaced_secret(namespace=namespace)

      secrets_list = [
          KubeResourceInfo(
              name=secret.metadata.name,
              ns=secret.metadata.namespace
          ) for secret in secrets.items
      ]

      logger.info(f"{len(secrets_list)} secrets encontradas em {namespace}")
      return secrets_list

  def get_secrets_data(self, name: str, namespace: str) -> Any:
      secret: Any = self.v1.read_namespaced_secret(name=name, namespace=namespace)
      data = secret.data or {}

      decoded = {
          key: b64decode(value).decode('utf-8')
          for key, value in data.items()
      }

      return decoded

  def delete_pods(self, namespace: str, pod_name: str):
      try:
          self.v1.delete_namespaced_pod(namespace=namespace, name=pod_name)
          logger.info(f"Deletando pod {pod_name}.")
      except ApiException as e:
          logger.error(f"Falha ao deletar {namespace}/{pod_name}: {e.reason}")

  def pod_logs(self, namespace: str, pod_name: str) -> Any:
      try:
          logs = self.v1.read_namespaced_pod_log(namespace=namespace, name=pod_name, tail_lines=300)
          logger.info(f"Retornando log de {pod_name}")

          return logs

      except ApiException as e:
          logger.error(f"Falha ao recuperar log do {pod_name}: {e.body}")

          return None
