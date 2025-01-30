# Monopoly 3D

# Packet Classification

### BasePacket

```json
{
  "data": {},
  "meta": {
    "tag": "packet_tag",
    "class": "packet_class"
  }
}
```

Packet meta is a list of values which both client and server use to authorize and verify incoming packets, and to provide different implementations to process them.

Packet tag is a string tag of client name in snake case, packet class is a classification of sender, whether it is a client or server

## Client Packets

### ClientPingPacket

```json
{
  "data": {
    "request": "message"
  },
  "meta": {
    "tag": "client_ping",
    "class": "client"
  }
}
```

Sends a simple text message to server in request field

## Server Packets

### ServerPingPacket

```json
{
  "data": {
    "response": "message"
  },
  "meta": {
    "tag": "server_ping",
    "class": "server"
  }
}
```

Sends a simple text message to client in response field
