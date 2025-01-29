# Monopoly 3D

# Packet Classification

### BasePacket

```json
{
  "data": {},
  "meta": {
    "id": "packet_id",
    "tag": "packet_tag",
    "type": "packet_type"
  }
}
```

Packet meta is a list of values which both client and server use to authorize and verify incoming packets, and to provide different implementations to process them

## Client Packets

### CreateGamePacket

```json
{
  "data": {
    "player_id": "UUID"
  },
  "meta": {
    "id": "0",
    "tag": "join_game",
    "type": "client"
  }
}
```

Sent when a player wants to join the game.

## Server Packets

### UpdateRecruitingGamePacket

```json
{
  "data": {
    "some_keys": "some_values"
  },
  "meta": {
    "id": "packet_id",
    "tag": "packet_tag",
    "type": "packet_type"
  }
}
```

Sent when all clients must update information about a non-started game they are joined in.
