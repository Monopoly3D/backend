from enum import StrEnum


class PacketClass(StrEnum):
    CLIENT = "client"
    SERVER = "server"
    ANY = "any"
