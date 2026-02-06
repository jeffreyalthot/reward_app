# Protocole NRP-1 (Node Relay Protocol) — version sûre

Ce document propose un protocole de découverte et de relais **légitime** entre nœuds.

> ⚠️ Je n'inclus pas de mécanisme furtif/non détectable, de contournement de routeur, ni d'injection cachée dans du trafic chiffré. Ces techniques sont abusives et non conformes. Le design ci-dessous reste robuste, observable et sécurisé.

## 1) Objectif

- Permettre à un nœud de découvrir d'autres nœuds du même protocole.
- Exposer un service local sur `0.0.0.0:8080`.
- Relayer automatiquement les annonces de topologie entre pairs.
- Fonctionner sans dépendance à un protocole propriétaire externe (uniquement TCP/UDP standards).

## 2) Architecture

Chaque nœud exécute 3 plans :

1. **Plan découverte (UDP 8080)**
   - Broadcast/multicast local des annonces signées `HELLO`.
   - Réponses `HELLO_ACK` avec capacités du nœud.
2. **Plan contrôle (TCP 8080)**
   - Session chiffrée TLS mutuelle (mTLS).
   - Échange `PEER_LIST`, `ROUTE_UPDATE`, `PING/PONG`.
3. **Plan données (TCP 8080 ou port annoncé)**
   - Relais applicatif (frames encapsulées avec identifiant de flux).

## 3) Types de messages

Format général (CBOR recommandé) :

```text
{
  version: 1,
  type: "HELLO" | "HELLO_ACK" | "PEER_LIST" | "ROUTE_UPDATE" | "RELAY_FRAME",
  node_id: <32 bytes>,
  ts_unix_ms: <int64>,
  ttl: <uint8>,
  nonce: <96 bits>,
  payload: <map>,
  sig: <Ed25519 signature>
}
```

Règles :
- `node_id` = hash de la clé publique (stable).
- Signature obligatoire pour tous les messages.
- `ttl` décrémente à chaque relais pour éviter les boucles.

## 4) Découverte

1. Au démarrage, un nœud envoie `HELLO` (UDP local + liste bootstrap statique).
2. Les pairs répondent `HELLO_ACK` avec :
   - endpoint TCP,
   - version,
   - charge,
   - sous-réseaux connus.
3. Le nœud établit ensuite N connexions TCP mTLS vers les pairs valides.
4. Les `PEER_LIST` sont propagés périodiquement (gossip).

## 5) Relais de topologie

- Algorithme : gossip + route map (coût = latence + perte).
- Chaque `ROUTE_UPDATE` contient :
  - destination `node_id`,
  - next-hop,
  - coût,
  - âge.
- Expiration des routes anciennes (ex. 90 s).

## 6) Exposition service 0.0.0.0:8080

Le service écoute sur :
- `0.0.0.0:8080/udp` (découverte),
- `0.0.0.0:8080/tcp` (contrôle + relais).

Les clients locaux peuvent se connecter au nœud; le nœud choisit un chemin vers le pair cible selon la table de routage.

## 7) Sécurité (obligatoire)

- mTLS (TLS 1.3) entre nœuds.
- Autorisation par liste de clés publiques (allowlist) ou CA privée.
- Anti-rejeu via `nonce` + fenêtre temporelle.
- Limitation de débit + preuve de travail légère optionnelle contre spam.
- Journalisation activée (audit).

## 8) Résilience réseau

- Reconnexion exponentielle avec jitter.
- Keepalive `PING/PONG`.
- Multipath : maintenir 2–3 routes actives par destination.
- Changement automatique de chemin si latence/perte dépassent un seuil.

## 9) Pseudocode minimal

```text
on_start():
  load_keys()
  bind_udp_tcp(0.0.0.0:8080)
  send_hello_broadcast()
  connect_bootstrap_peers()

on_hello(msg):
  if verify_sig(msg) and fresh(msg):
    send_hello_ack(msg.node_id)
    maybe_connect(msg.endpoint)

on_route_update(msg):
  if verify_sig(msg) and msg.ttl > 0:
    update_route_table(msg)
    relay(msg.ttl - 1)
```

## 10) Notes conformité

Un protocole « invisible » ou « non détectable sauf par certains nœuds » n'est pas un objectif de sécurité sain. Un protocole fiable doit être :
- chiffré,
- authentifié,
- traçable,
- administrable.
