# stats.py
# Responsible for tracking and storing all statistics during a capture session.
# This module acts as the "memory" of the analyzer — every parsed packet gets
# passed here so we can count protocols, track active IPs, measure data volume,
# and keep a rolling history of recent packets for the live display.
#
# In C++ terms, think of this as a class that holds your data structures:
# dictionaries (like unordered_map), lists (like vectors), and a deque (like std::deque).

from collections import defaultdict, deque
# defaultdict  — a dictionary that automatically creates a default value for missing keys.
#                We use it so we never have to check "does this key exist?" before incrementing.
#                defaultdict(int) means any new key starts at 0 automatically.
#
# deque        — a double-ended queue. We use it to store the most recent N packets.
#                It's more efficient than a list for this because we're constantly
#                adding to one end and dropping from the other (like a sliding window).
#                In C++ this is similar to std::deque.

from packet_parser import ParsedPacket
# We import ParsedPacket so Python knows what type of objects we're storing.
# This also helps Pylance give you autocomplete when accessing packet fields.


# How many packets to keep in the recent packets list at once.
# Once we hit this limit, the oldest packet is automatically dropped.
MAX_RECENT_PACKETS = 100


class PacketStats:
    """
    Tracks all live statistics for the current capture session.
    
    Every time a packet is captured and parsed, it gets passed to
    the update() method here. The display module then reads from
    this object to render the live dashboard.
    """

    def __init__(self):
        """
        Initialize all counters and data structures to their starting state.
        Called once when the capture session begins.
        """

        # Total number of packets captured this session
        self.total_packets: int = 0

        # Total bytes captured across all packets
        # Useful for showing how much data has moved through the network
        self.total_bytes: int = 0

        # Per-protocol packet counter
        # defaultdict(int) means accessing stats.protocol_counts["TCP"] for the
        # first time automatically returns 0 instead of raising a KeyError.
        # Example after some captures: {"TCP": 142, "UDP": 38, "DNS": 20}
        self.protocol_counts: dict = defaultdict(int)

        # Per-IP packet counter — tracks how many packets each IP address has sent
        # Used to find the "top talkers" on your network (most active IP addresses).
        # Example: {"192.168.1.5": 80, "8.8.8.8": 34}
        self.ip_counts: dict = defaultdict(int)

        # Per-IP byte counter — tracks total bytes sent by each IP address
        # Gives a better picture of bandwidth usage than packet count alone.
        # A single large packet counts more than ten tiny ones.
        self.ip_bytes: dict = defaultdict(int)

        # Rolling window of the most recent MAX_RECENT_PACKETS packets
        # deque(maxlen=100) automatically discards the oldest entry when full —
        # we never have to manually remove old packets ourselves.
        # This is what gets displayed in the live packet feed on the dashboard.
        self.recent_packets: deque = deque(maxlen=MAX_RECENT_PACKETS)

        # List of packet sizes over time, used to calculate the average packet size.
        # We store all sizes (not just a running sum) so we can calculate stats
        # like min, max, and average without re-scanning packets.
        self.packet_sizes: list = []


    def update(self, packet: ParsedPacket):
        """
        Receives a single ParsedPacket and updates all statistics.
        
        This is called once per captured packet, so it needs to be fast.
        All operations here are O(1) — no loops, no sorting.

        Args:
            packet (ParsedPacket): A parsed packet object from parser.py
        """

        # Increment the total packet counter by 1
        self.total_packets += 1

        # Add this packet's byte size to the running total
        self.total_bytes += packet.size

        # Increment the count for this packet's protocol (e.g. "TCP", "UDP")
        # defaultdict means this works even if we've never seen this protocol before
        self.protocol_counts[packet.protocol] += 1

        # Increment the packet count for the source IP address
        # This tells us which IPs are sending the most packets
        self.ip_counts[packet.src_ip] += 1

        # Add the packet's byte size to the source IP's total byte usage
        # This tells us which IPs are consuming the most bandwidth
        self.ip_bytes[packet.src_ip] += packet.size

        # Append the full ParsedPacket object to the recent packets window
        # When deque hits maxlen=100, the oldest packet is automatically removed
        self.recent_packets.append(packet)

        # Store the packet size separately for average/min/max calculations
        self.packet_sizes.append(packet.size)


    def get_top_ips(self, n: int = 5) -> list[tuple[str, int]]:
        """
        Returns the top N IP addresses by packet count.
        
        Uses Python's sorted() with a lambda as the sort key.
        
        sorted() args:
            iterable  — self.ip_counts.items() gives us (ip, count) pairs
            key       — lambda tells sorted() to sort by the count (index 1 of the tuple)
            reverse   — True means highest count comes first (descending order)
        
        [:n] slices the sorted list to only return the top N results.

        Args:
            n (int): How many top IPs to return. Defaults to 5.

        Returns:
            list of (ip_address, packet_count) tuples, sorted by count descending.
            Example: [("192.168.1.5", 80), ("8.8.8.8", 34), ("10.0.0.1", 12)]
        """
        return sorted(self.ip_counts.items(), key=lambda x: x[1], reverse=True)[:n]


    def get_average_packet_size(self) -> float:
        """
        Calculates the average size of all captured packets in bytes.
        
        sum()  — adds up every value in the packet_sizes list
        len()  — returns how many items are in the list
        
        We guard against dividing by zero by returning 0.0 if no packets
        have been captured yet (empty list has len() == 0).

        Returns:
            float: Average packet size in bytes, or 0.0 if no packets captured.
        """

        # Guard: avoid ZeroDivisionError if no packets have been captured yet
        if not self.packet_sizes:
            return 0.0

        # sum() adds up all values, len() counts them — standard average formula
        return sum(self.packet_sizes) / len(self.packet_sizes)


    def get_protocol_percentage(self, protocol: str) -> float:
        """
        Returns what percentage of total traffic a given protocol makes up.
        
        Args:
            protocol (str): The protocol name to check, e.g. "TCP", "UDP", "DNS"

        Returns:
            float: Percentage from 0.0 to 100.0, or 0.0 if no packets captured.
            Example: 74.3 means 74.3% of all packets were this protocol.
        """

        # Guard: avoid ZeroDivisionError if no packets have been captured yet
        if self.total_packets == 0:
            return 0.0

        # self.protocol_counts[protocol] safely returns 0 for unknown protocols
        # because it's a defaultdict(int)
        return (self.protocol_counts[protocol] / self.total_packets) * 100


    def reset(self):
        """
        Resets all statistics back to zero.
        Called when the user starts a new capture session without restarting
        the program. Re-runs __init__() to cleanly wipe all data structures.
        """

        # Calling __init__() again is a clean way to reset all instance variables
        # to their original starting state without duplicating the setup code.
        self.__init__()