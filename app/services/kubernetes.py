from typing import Dict
from typing import NamedTuple, Any, Optional
from kubernetes import client, config
from kubernetes.client import ApiException
from app.utils.logger import logger
from base64 import b64decode

class KubeResourceInfo(NamedTuple):
    name: str
    ns: Optional[str] = None
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

  def get_pods(self, namespace: str, label: Optional[str] = None) -> Optional[list[KubeResourceInfo]]:
    try:
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

    except ApiException as e:
      logger.error(f"Erro ao recuperar pods! {e.reason}: {e.body}")
      return None

  def get_secrets(self, namespace: str) -> Optional[list[KubeResourceInfo]]:
    try:
      secrets = self.v1.list_namespaced_secret(namespace=namespace)

      secrets_list = [
          KubeResourceInfo(
              name=secret.metadata.name,
              ns=secret.metadata.namespace
          ) for secret in secrets.items
      ]

      logger.info(f"{len(secrets_list)} secrets encontradas em {namespace}")
      return secrets_list

    except ApiException as e:
      logger.error(f"Erro ao recuperar secrets! {e.reason}: {e.body}")
      return None

  def get_secrets_data(self, name: str, namespace: str) -> Optional[Dict[str, str]]:
    try:
      secret: Any = self.v1.read_namespaced_secret(name=name, namespace=namespace)
      data = secret.data or {}

      decoded = {
          key: b64decode(value).decode('utf-8')
          for key, value in data.items()
      }

      return decoded

    except ApiException as e:
      logger.error(f"Erro ao recuperar dados da secret! {e.reason}: {e.body}")
      return None

  def delete_pods(self, namespace: str, pod_name: str):
      try:
          self.v1.delete_namespaced_pod(namespace=namespace, name=pod_name)
          logger.info(f"Deletando pod {pod_name}.")
      except ApiException as e:
          logger.error(f"Falha ao deletar {namespace}/{pod_name}! {e.reason}: {e.body}")

  def pod_logs(self, namespace: str, pod_name: str) -> Optional[str]:
      try:
          logs = self.v1.read_namespaced_pod_log(namespace=namespace, name=pod_name, tail_lines=300)
          logger.info(f"Retornando log de {pod_name}")
          return logs

      except ApiException as e:
          logger.error(f"Falha ao recuperar log do {pod_name}! {e.reason}: {e.body}")
          return None

  def get_config_map(self, namespace: str) -> Optional[list[KubeResourceInfo]]:
    try:
      config_maps = self.v1.list_namespaced_config_map(namespace=namespace)

      config_maps_list = [
        KubeResourceInfo(
            name=cm.metadata.name,
            ns=cm.metadata.namespace
        ) for cm in config_maps.items
      ]

      logger.info(f"{len(config_maps_list)} encontrados em {namespace}")
      return config_maps_list

    except ApiException as e:
      logger.error(f"Erro ao recuperar ConfigMaps! {e.reason}: {e.body}")
      return None

  def get_config_map_data(self, name: str, namespace: str) -> Optional[Dict[str, str]]:
    try:
      config_map: Any = self.v1.read_namespaced_config_map(name=name, namespace=namespace)
      data = config_map.data or {}

      data_formatted = {
        key: value
        for key, value in data.items()
      }

      return data_formatted

    except ApiException as e:
      logger.error(f"Erro ao recuperar dados do ConfigMap! {e.reason}: {e.body}")
      return None

  def get_namespaces(self) -> Optional[list[KubeResourceInfo]]:
    try:
      namespaces = self.v1.list_namespace()

      namespace_list = [
        KubeResourceInfo(
          name=ns.metadata.name
        ) for ns in namespaces.items
      ]

      return namespace_list

    except ApiException as e:
      logger.error(f"Erro ao recuperar Namespaces! {e.reason}: {e.body}")
      return None
