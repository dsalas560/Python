# capture.py
# Responsible for starting, stopping, and managing the packet capture session.
# This is the module that actually interfaces with your network hardware through
# Scapy and Npcap. It acts as the "engine" of the analyzer — pulling raw packets
# off the network interface and feeding them through the parser and stats pipeline.
#
# Flow:
#   capture.py grabs a raw packet
#       → sends it to parser.py to decode it
#           → sends the decoded packet to stats.py to record it
#               → display.py reads stats and redraws the dashboard

import scapy.all as scapy
# scapy.all imports the full Scapy library.
# We use it to:
#   - List available network interfaces (scapy.get_if_list())
#   - Start packet capture (scapy.sniff())
# Scapy communicates with Npcap on Windows to access raw network traffic.

import threading
# threading allows us to run the packet capture in a background thread
# while the main thread handles the live display.
# Without threading, the display would freeze while waiting for packets,
# or packets would be missed while the display is rendering.
# In C++ terms, think of this like std::thread.

import time
# time.sleep() is used in the capture loop to avoid busy-waiting
# and to give the display thread time to render between updates.

from packet_parser import parse_packet
# parse_packet() takes a raw Scapy packet and returns a ParsedPacket object.
# If the packet type isn't one we handle, it returns None.

from stats import PacketStats
# PacketStats is our central data store. We pass it into the capture
# function so it can be updated as packets arrive.

from display import build_layout, create_live_display
# build_layout() assembles the full dashboard from the current stats.
# create_live_display() gives us the Rich Live context manager.


def get_interfaces() -> list[str]:
    """
    Returns a list of all available network interfaces on this machine.
    
    scapy.get_if_list() calls into Npcap (on Windows) to enumerate
    every network adapter available — including ethernet, WiFi,
    loopback, and virtual adapters.

    Returns:
        list[str]: A list of interface name strings.
        Example: ['Ethernet', 'Wi-Fi', 'Loopback Pseudo-Interface 1']
    """

    # get_if_list() queries Npcap for all available interfaces.
    # Returns raw adapter names that we display to the user for selection.
    return scapy.get_if_list()


def select_interface() -> str:
    """
    Interactively prompts the user to select a network interface to capture on.
    
    Lists all available interfaces with a number next to each one,
    then waits for the user to enter their choice. Keeps asking until
    a valid number is entered.

    Returns:
        str: The name of the selected interface.
        Example: 'Wi-Fi'
    """

    interfaces = get_interfaces()

    print("\n[+] Available Network Interfaces:\n")

    # enumerate(interfaces) gives us (index, value) pairs starting at 1.
    # We use this to number the list for the user: 1, 2, 3...
    for i, iface in enumerate(interfaces, start=1):
        print(f"    {i}. {iface}")

    print()

    # Keep prompting until the user enters a valid number
    while True:
        try:
            # input() reads a string from the terminal.
            # int() converts it to an integer — raises ValueError if not a number.
            choice = int(input("[?] Select interface number: "))

            # Check that the number is within the valid range
            if 1 <= choice <= len(interfaces):
                # Lists are zero-indexed, so we subtract 1 from the user's choice
                selected = interfaces[choice - 1]
                print(f"\n[+] Selected: {selected}\n")
                return selected
            else:
                print(f"[!] Please enter a number between 1 and {len(interfaces)}")

        except ValueError:
            # Raised when the user types something that isn't a number
            print("[!] Invalid input. Please enter a number.")


def packet_callback(packet, stats: PacketStats):
    """
    Called automatically by Scapy once for every packet captured.
    
    This is a callback function — we pass it to scapy.sniff() and
    Scapy calls it each time a new packet arrives on the interface.
    In C++ terms, think of this like a function pointer or a handler.
    
    Flow:
        1. Scapy captures a raw packet from the network
        2. Scapy calls this function with the packet
        3. We send it to parse_packet() to decode it
        4. If it's a packet type we care about, we update the stats
        5. The display thread reads the updated stats on its next refresh

    Args:
        packet:             Raw Scapy packet object straight off the wire.
        stats (PacketStats): The shared stats object to update.
    """

    # parse_packet() attempts to decode the raw packet.
    # Returns a ParsedPacket if successful, or None if we don't handle that type.
    parsed = parse_packet(packet)

    # Only update stats if we successfully parsed the packet.
    # Unparsed packets (like raw Ethernet frames) are silently ignored.
    if parsed:
        stats.update(parsed)


def start_capture(interface: str, stats: PacketStats, stop_event: threading.Event):
    """
    Starts the packet capture loop on the given interface.
    
    Runs in a background thread. Continues capturing until stop_event
    is set (which happens when the user presses Ctrl+C).

    scapy.sniff() args:
        iface    — the network interface to capture on (e.g. 'Wi-Fi')
        prn      — callback function called for every captured packet.
                   We use a lambda to pass the stats object along with
                   each packet, since prn only passes the packet by default.
        store    — False means Scapy does NOT store packets in memory.
                   This is important — without this, Scapy accumulates every
                   packet in a list and will eventually consume all your RAM.
        stop_filter — a function called after each packet. If it returns True,
                      sniff() stops capturing. We check stop_event.is_set()
                      which becomes True when the user presses Ctrl+C.

    Args:
        interface (str):            Name of the network interface to capture on.
        stats (PacketStats):        Shared stats object updated on each packet.
        stop_event (threading.Event): Event flag used to signal capture to stop.
    """

    scapy.sniff(
        iface=interface,

        # prn is called for every packet. Lambda lets us pass stats along
        # since scapy.sniff() only gives prn the raw packet by default.
        prn=lambda pkt: packet_callback(pkt, stats),

        # store=False tells Scapy not to keep packets in memory.
        # Essential for long captures — without this RAM usage grows forever.
        store=False,

        # stop_filter is checked after each packet.
        # stop_event.is_set() returns True once we call stop_event.set()
        # in the main run() function when the user presses Ctrl+C.
        stop_filter=lambda _: stop_event.is_set()
    )


def run():
    """
    Main entry point for the capture session.
    
    Orchestrates the full lifecycle:
        1. Ask user to select a network interface
        2. Initialize the stats object
        3. Start the packet capture in a background thread
        4. Run the live display on the main thread
        5. On Ctrl+C, signal the capture thread to stop and exit cleanly

    Threading model:
        - Main thread   → runs the Rich live display (refreshes every 0.25s)
        - Capture thread → runs scapy.sniff() and updates stats on every packet

    We use a threading.Event as a shared flag between the two threads.
    When the user presses Ctrl+C, we set the event which tells the
    capture thread to stop on its next packet.
    """

    # Step 1 — Let the user pick which network interface to sniff on
    interface = select_interface()

    # Step 2 — Create a fresh stats object for this session
    stats = PacketStats()

    # Step 3 — Create a threading.Event to coordinate shutdown between threads.
    # threading.Event is a simple thread-safe boolean flag.
    #   stop_event.set()      → sets the flag to True
    #   stop_event.is_set()   → returns True if the flag has been set
    #   stop_event.clear()    → resets the flag to False
    stop_event = threading.Event()

    # Step 4 — Create the capture thread.
    # threading.Thread() args:
    #   target — the function to run in the new thread
    #   args   — tuple of arguments to pass to target
    #   daemon — True means this thread will be automatically killed
    #            when the main thread exits, so we never get a zombie thread
    #            hanging around after the program ends.
    capture_thread = threading.Thread(
        target=start_capture,
        args=(interface, stats, stop_event),
        daemon=True     # Auto-killed when main thread exits
    )

    # .start() launches the thread — start_capture() begins running
    # in the background immediately after this line.
    capture_thread.start()

    print(f"[+] Capturing on {interface} — Press Ctrl+C to stop\n")

    # Step 5 — Run the live display on the main thread.
    # create_live_display() returns a Rich Live object.
    # The "with" block starts the Live context — Rich takes control of
    # the terminal output for the duration of this block.
    try:
        with create_live_display() as live:
            # Keep refreshing the display until Ctrl+C is pressed.
            # Each iteration rebuilds the full dashboard from current stats.
            while not stop_event.is_set():

                # build_layout() reads all current stats and assembles
                # the full dashboard as a Rich renderable.
                # live.update() pushes it to the terminal.
                live.update(build_layout(stats))

                # Sleep 0.25 seconds between redraws (4 frames per second).
                # time.sleep() releases the thread so the OS can do other work.
                # Without this the main thread would spin at 100% CPU.
                time.sleep(0.25)

    except KeyboardInterrupt:
        # Ctrl+C raises KeyboardInterrupt in Python.
        # We catch it here to perform a clean shutdown instead of a crash.
        pass

    finally:
        # The finally block ALWAYS runs, whether we got a KeyboardInterrupt
        # or exited normally. This guarantees the capture thread is stopped.

        # Signal the capture thread to stop on its next packet
        stop_event.set()

        # .join() blocks the main thread until the capture thread fully exits.
        # timeout=2 means we wait at most 2 seconds before giving up.
        # This prevents the program from hanging if a packet never arrives.
        capture_thread.join(timeout=2)

        print("\n[+] Capture stopped.")
        print(f"[+] Total packets captured: {stats.total_packets}")
        print(f"[+] Total data captured: {stats.total_bytes} bytes")
