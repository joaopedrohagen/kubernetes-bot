# Kubernetes Bot (Telegram)

Este é um bot para Telegram que integra a API do Kubernetes para **reiniciar** e **listar** os pods.

## Funcionalidades

- Lista os pods em um namespace
- Reinicia pods individualmente com um botão `Restart`
- Utiliza API do Kubernetes
- Interação simples e direta via Telegram

---

## Utilização

```bash
/pod_status <namespace>
/list_secrets <namespace>
```

Exemplo:

```bash
/pod_status prod
/list_secrets dev
```

O bot vai listar os recursos do namespace `prod` e dará as opções com botões para cada um.

### Reiniciar um pod

- Clique no botão **"Restart"** abaixo da mensagem do pod desejado.
- O pod será deletado via API do Kubernetes (ele será recriado automaticamente se houver um ReplicaSet ou Deployment).

### Visualizar logs
- Clique no botão **"Logs"** abaixo da mensagem do pod.
- Serão retornados os logs do serviço selecionado.

---

## Configuração

### Pré-requisitos

- Python 3.10+
- Kubernetes cluster acessível via `kubeconfig` (Se você executar dentro do Cluster, o pod utiliza o ServiceAccount)
- Token do Bot do Telegram

### Variáveis de ambiente

Crie um arquivo `app/.secrets.toml` com as seguintes chaves:

```env
[default]
TELEGRAM_BOT_TOKEN=<seu_token_do_bot>
```

### Instalação

```bash
git clone https://github.com/joaopedrohagen/kubernetes-bot.git
cd kubernetes-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Executando o bot

```bash
python -m app.main
```

---

## Aviso

> Este bot **deleta pods** diretamente no cluster Kubernetes. Use com precaução e configure RBAC adequadamente!

---

## Licença

[MIT](LICENSE)
