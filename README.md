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

Packet tag is a string tag of client name in snake case, packet class is a classification of sender, whether it is a client or server.

## Client Packets

### ClientAuthPacket

```json
{
  "data": {
    "ticket": "JWT-encoded ticket"
  },
  "meta": {
    "tag": "client_auth",
    "class": "client"
  }
}
```

Authenticates client, must be the first packet sent to server, otherwise server will close the connection.

Ticket field is a JWT-encoded token that currently authenticates client by user ID, client must get this ticket by sending a specific HTTP request.

### ClientJoinGamePacket

```json
{
  "data": {
    "game_id": "UUID"
  },
  "meta": {
    "tag": "client_join_game",
    "class": "client"
  }
}
```

Sends a simple text message to server in request field.

### ClientPingPacket

```json
{
  "data": {
    "request": "Message"
  },
  "meta": {
    "tag": "client_ping",
    "class": "client"
  }
}
```

Sends a simple text message to server in request field.

## Server Packets

### ServerAuthResponsePacket

```json
{
  "data": {
    "user_id": "UUID",
    "username": "Plummy"
  },
  "meta": {
    "tag": "server_auth_response",
    "class": "server"
  }
}
```

Sends a response if the authentication succeeded, otherwise server closes the connection with code 3000.

### ServerErrorPacket

```json
{
  "data": {
    "status": 4000,
    "detail": "Error detail"
  },
  "meta": {
    "tag": "server_error",
    "class": "server"
  }
}
```

Sends an exception status code and detail.

### ServerPingPacket

```json
{
  "data": {
    "response": "Message"
  },
  "meta": {
    "tag": "server_ping",
    "class": "server"
  }
}
```

Sends a simple text message to client in response field.
