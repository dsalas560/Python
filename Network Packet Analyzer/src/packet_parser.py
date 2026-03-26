# packet_parser.py
# Responsible for taking raw Scapy packets and converting them into
# clean, structured ParsedPacket objects that the rest of the app can use.

from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.l2 import ARP, Ether
from scapy.layers.dns import DNS
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ParsedPacket:
    timestamp: str
    protocol: str
    src_ip: str
    dst_ip: str
    src_port: int | None
    dst_port: int | None
    size: int
    info: str


def parse_packet(packet) -> ParsedPacket | None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    size = len(packet)

    if packet.haslayer(ARP):
        arp = packet[ARP]
        return ParsedPacket(
            timestamp=timestamp,
            protocol="ARP",
            src_ip=arp.psrc,
            dst_ip=arp.pdst,
            src_port=None,
            dst_port=None,
            size=size,
            info=f"{'Who has' if arp.op == 1 else 'Is at'} {arp.pdst}"
        )

    if not packet.haslayer(IP):
        return None

    ip = packet[IP]
    src_ip = ip.src
    dst_ip = ip.dst

    if packet.haslayer(DNS):
        dns = packet[DNS]
        query = dns.qd.qname.decode() if dns.qd else "unknown"
        direction = "Query" if dns.qr == 0 else "Response"
        return ParsedPacket(
            timestamp=timestamp,
            protocol="DNS",
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=53,
            dst_port=53,
            size=size,
            info=f"{direction}: {query}"
        )

    if packet.haslayer(TCP):
        tcp = packet[TCP]
        flags = parse_tcp_flags(tcp.flags)
        return ParsedPacket(
            timestamp=timestamp,
            protocol="TCP",
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=tcp.sport,
            dst_port=tcp.dport,
            size=size,
            info=f"Flags: {flags}"
        )

    if packet.haslayer(UDP):
        udp = packet[UDP]
        return ParsedPacket(
            timestamp=timestamp,
            protocol="UDP",
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=udp.sport,
            dst_port=udp.dport,
            size=size,
            info=f"Port {udp.sport} → {udp.dport}"
        )

    if packet.haslayer(ICMP):
        icmp = packet[ICMP]
        icmp_types = {0: "Echo Reply", 8: "Echo Request", 3: "Dest Unreachable"}
        info = icmp_types.get(icmp.type, f"Type {icmp.type}")
        return ParsedPacket(
            timestamp=timestamp,
            protocol="ICMP",
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=None,
            dst_port=None,
            size=size,
            info=info
        )

    return None


def parse_tcp_flags(flags) -> str:
    flag_map = {
        "F": "FIN",
        "S": "SYN",
        "R": "RST",
        "P": "PSH",
        "A": "ACK",
        "U": "URG",
    }
    return " ".join(flag_map[f] for f in flag_map if f in str(flags)) or "NONE"