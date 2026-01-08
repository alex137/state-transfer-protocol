# Example: Provider↔Hub Endpoint Exchange Using STP + Notify

This example shows how two participants exchange relationship endpoints using:

- an **STP manifest table** (`schema=endpoint_manifest`)
- a **notify URL** to announce availability and changes

> Note: This is an application pattern. It is **not** required by STP itself.

---

## Actors

- **Provider**
- **Hub**
- Hub has a known URL: `Hub_User_Endpoint_URL` (a notify endpoint)

---

## Step 1 — Provider announces its manifest table

Provider POSTs to the hub notify endpoint:

```
POST Hub_User_Endpoint_URL
Content-Type: application/x-www-form-urlencoded

table=https://prov.com/manifest
```

(Provider may send this on initial discovery and whenever its manifest changes.)

---

## Step 2 — Hub fetches provider manifest

```
GET https://prov.com/manifest?since_id=0
Accept: text/sequence
```

Response:

```
1\t2026-01-08T00:00:00Z\t+\tfhir_subscribe\thttps://prov.com/fhir/sub
2\t2026-01-08T00:00:00Z\t+\tfhir_read\thttps://prov.com/fhir/read
3\t2026-01-08T00:00:00Z\t+\tdirect_message\thttps://prov.com/direct
4\t2026-01-08T00:00:00Z\t+\tmanifest_notify\thttps://prov.com/notify
```

Content-Type:

```
text/sequence; charset=utf-8; schema=endpoint_manifest; version=1
```

---

## Step 3 — Provider fetches hub manifest

Provider GETs the hub’s manifest table (hub exposes it as an STP table URL):

```
GET https://hub.com/user/123/manifest?since_id=0
```

---

## Step 4 — Change propagation

If hub endpoints change, the hub notifies the provider:

```
POST https://prov.com/notify
Content-Type: application/x-www-form-urlencoded

table=https://hub.com/user/123/manifest
```

Provider re-GETs the hub manifest using its last seen SeqNo:

```
GET https://hub.com/user/123/manifest?since_id=<last_seen>
```

The manifest table remains authoritative.
