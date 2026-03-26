# display.py
# Responsible for rendering the live terminal dashboard using the Rich library.
# This module reads from the PacketStats object and redraws the screen on every
# update — similar to how a game engine redraws a frame.
#
# Rich gives us colored text, tables, panels, and layouts that update in place
# without the terminal scrolling. Think of it as a terminal UI framework.

from rich.console import Console
# Console — Rich's main output object. All rendering goes through this.
# It handles color, width detection, and writing to the terminal.

from rich.table import Table
# Table — creates formatted tables with headers, borders, and colored cells.
# We use this to display the live packet feed and top IPs list.

from rich.panel import Panel
# Panel — wraps content in a bordered box with an optional title.
# We use panels to group related stats together visually.

from rich.layout import Layout
# Layout — divides the terminal into named regions (like a grid).
# We split the screen into sections: header, stats, packet feed, footer.

from rich.live import Live
# Live — the key Rich class that enables real-time updating displays.
# It redraws the terminal in place without scrolling, like a dashboard.
# Under the hood it uses ANSI escape codes to move the cursor and redraw.

from rich.text import Text
# Text — a Rich string that can have mixed colors and styles inline.
# We use it to color-code protocol names (TCP=blue, DNS=green, etc.)

from rich.columns import Columns
# Columns — arranges multiple renderables side by side horizontally.
# We use this to place stat panels next to each other.

from rich import box
# box — provides different border styles for tables and panels.
# box.SIMPLE, box.ROUNDED, box.HEAVY etc. We use box.SIMPLE for clean output.

from stats import PacketStats
# We import PacketStats so Pylance knows the type and gives us autocomplete
# when we access stats fields like stats.total_packets, stats.protocol_counts, etc.


# --- Protocol Color Map ---
# Maps each protocol name to a Rich color string.
# These colors are used throughout the display to make protocols visually distinct.
# Rich color names follow the standard terminal 256-color naming convention.
PROTOCOL_COLORS = {
    "TCP":  "bright_blue",
    "UDP":  "bright_yellow",
    "DNS":  "bright_green",
    "ICMP": "bright_magenta",
    "ARP":  "bright_cyan",
}

# Fallback color for any protocol not in the map above
DEFAULT_COLOR = "white"


def get_protocol_color(protocol: str) -> str:
    """
    Returns the Rich color string for a given protocol name.
    
    dict.get(key, default) — looks up the key in the dictionary and returns
    the value if found, or the default value if the key doesn't exist.
    This avoids a KeyError if we encounter an unexpected protocol.

    Args:
        protocol (str): Protocol name e.g. "TCP", "UDP"

    Returns:
        str: A Rich-compatible color name e.g. "bright_blue"
    """
    return PROTOCOL_COLORS.get(protocol, DEFAULT_COLOR)


def build_header() -> Panel:
    """
    Builds the top header panel showing the app title and status.
    
    Panel() args:
        renderable — the content to display inside the panel (a Text object here)
        style      — border color of the panel
        padding    — (top/bottom, left/right) space inside the panel edges

    Returns:
        Panel: A Rich Panel object ready to be rendered.
    """

    # Text() creates a styled string. justify="center" centers it in the panel.
    title = Text("Network Packet Analyzer", justify="center")

    # .stylize(style, start, end) applies a style to a character range.
    # Here we make the entire string bold bright_green (indices 0 to end).
    title.stylize("bold bright_green")

    subtitle = Text("Live Capture Dashboard  |  Press Ctrl+C to stop", justify="center")
    subtitle.stylize("dim white")

    # "\n".join() combines the title and subtitle with a newline between them.
    # We render both as a combined text block inside the panel.
    return Panel(
        Text.assemble(title, "\n", subtitle),
        style="green",
        padding=(1, 2)
    )


def build_stats_panels(stats: PacketStats) -> Columns:
    """
    Builds a row of stat panels showing key metrics side by side.
    
    Each Panel shows one metric: total packets, total bytes, 
    average packet size, and most active protocol.

    Columns() takes a list of renderables and displays them
    horizontally side by side, evenly spaced.

    Args:
        stats (PacketStats): The current session's statistics object.

    Returns:
        Columns: A Rich Columns object containing all stat panels side by side.
    """

    # --- Most Active Protocol ---
    # max() with a key finds the item in the iterable with the highest value.
    # stats.protocol_counts.items() gives (protocol, count) pairs.
    # key=lambda x: x[1] tells max() to compare by the count (second element).
    # If no packets yet, we default to "N/A" to avoid an error on an empty dict.
    top_protocol = (
        max(stats.protocol_counts.items(), key=lambda x: x[1])[0]
        if stats.protocol_counts
        else "N/A"
    )

    # --- Format Total Bytes ---
    # We display bytes in KB if over 1024, otherwise raw bytes.
    # This makes large numbers more readable (e.g. "142.3 KB" vs "145715 B").
    if stats.total_bytes >= 1024:
        # Round to 1 decimal place using :.1f format specifier
        bytes_display = f"{stats.total_bytes / 1024:.1f} KB"
    else:
        bytes_display = f"{stats.total_bytes} B"

    # Build each stat as its own Panel with a title and centered content.
    # Text(str, justify, style) creates a colored centered value inside each panel.
    panels = [
        Panel(
            Text(str(stats.total_packets), justify="center", style="bold bright_cyan"),
            title="[dim]Packets Captured[/dim]",
            border_style="cyan",
            padding=(1, 4)
        ),
        Panel(
            Text(bytes_display, justify="center", style="bold bright_yellow"),
            title="[dim]Data Captured[/dim]",
            border_style="yellow",
            padding=(1, 4)
        ),
        Panel(
            # :.1f formats the float to 1 decimal place e.g. "142.3"
            Text(f"{stats.get_average_packet_size():.1f} B", justify="center", style="bold bright_magenta"),
            title="[dim]Avg Packet Size[/dim]",
            border_style="magenta",
            padding=(1, 4)
        ),
        Panel(
            Text(
                top_protocol,
                justify="center",
                # Color the top protocol using our protocol color map
                style=f"bold {get_protocol_color(top_protocol)}"
            ),
            title="[dim]Top Protocol[/dim]",
            border_style="green",
            padding=(1, 4)
        ),
    ]

    # Columns() arranges the list of panels horizontally.
    # equal=True makes each panel take up the same width.
    return Columns(panels, equal=True)


def build_protocol_table(stats: PacketStats) -> Panel:
    """
    Builds a table showing packet count and percentage for each protocol seen.

    Table() args:
        box       — border style (box.SIMPLE = minimal lines, clean look)
        show_edge — whether to draw the outer border of the table
        padding   — cell padding (top/bottom, left/right)

    Args:
        stats (PacketStats): The current session's statistics object.

    Returns:
        Panel: A panel containing the protocol breakdown table.
    """

    # Create the table with column headers
    table = Table(
        box=box.SIMPLE,
        show_edge=False,    # No outer border — cleaner look inside a panel
        padding=(0, 1),
        header_style="bold white"
    )

    # add_column() defines each column header and its alignment/style.
    # style applies to all data cells in that column.
    # justify controls text alignment: "left", "right", "center"
    table.add_column("Protocol", style="bold", justify="left")
    table.add_column("Packets",  justify="right")
    table.add_column("Percent",  justify="right")
    table.add_column("Bar",      justify="left", no_wrap=True)

    # Sort protocols by packet count descending so the most active is at the top.
    # sorted() returns a new list — it doesn't modify protocol_counts in place.
    # key=lambda x: x[1] sorts by the count value, reverse=True = highest first.
    sorted_protocols = sorted(
        stats.protocol_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for protocol, count in sorted_protocols:
        # Get this protocol's percentage of total traffic
        percentage = stats.get_protocol_percentage(protocol)

        # Build a simple ASCII bar chart scaled to 20 characters wide.
        # int(percentage / 5) converts 0-100% to 0-20 bar segments.
        # "█" * n repeats the block character n times to form the bar.
        bar_length = int(percentage / 5)
        bar = "█" * bar_length

        color = get_protocol_color(protocol)

        # add_row() adds one row to the table.
        # Rich markup [color]text[/color] applies inline color to a string.
        table.add_row(
            f"[{color}]{protocol}[/{color}]",
            f"[{color}]{count}[/{color}]",
            f"[{color}]{percentage:.1f}%[/{color}]",
            f"[{color}]{bar}[/{color}]"
        )

    return Panel(table, title="[bold]Protocol Breakdown[/bold]", border_style="blue")


def build_top_ips_table(stats: PacketStats) -> Panel:
    """
    Builds a table showing the top 5 most active IP addresses by packet count.

    Args:
        stats (PacketStats): The current session's statistics object.

    Returns:
        Panel: A panel containing the top IPs table.
    """

    table = Table(
        box=box.SIMPLE,
        show_edge=False,
        padding=(0, 1),
        header_style="bold white"
    )

    table.add_column("IP Address", justify="left",  style="bright_white")
    table.add_column("Packets",    justify="right", style="bright_cyan")
    table.add_column("Bytes",      justify="right", style="bright_yellow")

    # get_top_ips(5) returns the 5 most active IPs as (ip, count) tuples
    for ip, count in stats.get_top_ips(5):

        # Look up byte usage for this IP from the ip_bytes dict.
        # .get(ip, 0) safely returns 0 if the IP somehow isn't in ip_bytes.
        bytes_used = stats.ip_bytes.get(ip, 0)

        # Format bytes as KB if large enough, same logic as in build_stats_panels
        if bytes_used >= 1024:
            bytes_display = f"{bytes_used / 1024:.1f} KB"
        else:
            bytes_display = f"{bytes_used} B"

        table.add_row(ip, str(count), bytes_display)

    return Panel(table, title="[bold]Top IP Addresses[/bold]", border_style="yellow")


def build_packet_feed(stats: PacketStats) -> Panel:
    """
    Builds a scrolling table of the most recent captured packets.
    
    Reads from stats.recent_packets which is a deque capped at 100 entries.
    We show the most recent 15 for a clean feed without overwhelming the terminal.

    Args:
        stats (PacketStats): The current session's statistics object.

    Returns:
        Panel: A panel containing the recent packet feed table.
    """

    table = Table(
        box=box.SIMPLE,
        show_edge=False,
        padding=(0, 1),
        header_style="bold white"
    )

    table.add_column("Time",     justify="left",  style="dim white",    width=10)
    table.add_column("Protocol", justify="center",                      width=8)
    table.add_column("Source",   justify="left",  style="bright_white", width=18)
    table.add_column("→ Dest",   justify="left",  style="bright_white", width=18)
    table.add_column("Size",     justify="right", style="bright_yellow", width=8)
    table.add_column("Info",     justify="left",  style="dim white")

    # list() converts the deque to a list so we can slice it.
    # [-15:] takes the last 15 entries (most recent).
    # reversed() flips the order so newest appears at the top.
    recent = list(reversed(list(stats.recent_packets)[-15:]))

    for packet in recent:
        color = get_protocol_color(packet.protocol)

        # Format the destination to include port number if available.
        # e.g. "8.8.8.8:443" for TCP, or just "8.8.8.8" for ICMP.
        dst = (
            f"{packet.dst_ip}:{packet.dst_port}"
            if packet.dst_port
            else packet.dst_ip
        )

        src = (
            f"{packet.src_ip}:{packet.src_port}"
            if packet.src_port
            else packet.src_ip
        )

        table.add_row(
            packet.timestamp,
            f"[{color}]{packet.protocol}[/{color}]",
            src,
            dst,
            f"{packet.size}B",
            packet.info
        )

    return Panel(table, title="[bold]Live Packet Feed[/bold]", border_style="bright_blue")


def build_layout(stats: PacketStats):
    """
    Assembles all panels into one complete dashboard layout.
    
    This is the function called on every refresh cycle. It builds
    every component fresh and stacks them vertically for display.
    
    Rich doesn't require a grid system here — stacking renderables
    in a list and printing them sequentially gives us a clean top-to-bottom
    dashboard layout within the Live context.

    Args:
        stats (PacketStats): The current session's statistics object.

    Returns:
        A list of Rich renderables stacked top to bottom.
    """
    from rich.console import Group
    # Group — combines multiple renderables into one so Live can render
    # them together as a single unit on each refresh.

    return Group(
        build_header(),
        build_stats_panels(stats),
        build_protocol_table(stats),
        build_top_ips_table(stats),
        build_packet_feed(stats),
    )


# --- Live Display Context ---
# We expose the Rich Live object so capture.py can use it as a context manager.
# This is created once and reused across the whole session.
#
# Live() args:
#   refresh_per_second — how many times per second Rich redraws the dashboard.
#                        4 gives a smooth feel without hammering the CPU.
#   screen             — False means we don't take over the full terminal screen,
#                        just print below whatever is already there.
def create_live_display() -> Live:
    """
    Creates and returns a configured Rich Live display object.
    
    The Live object is used as a context manager in capture.py:
        with create_live_display() as live:
            live.update(build_layout(stats))
    
    Returns:
        Live: A configured Rich Live instance ready to be used as a context manager.
    """
    return Live(
        refresh_per_second=4,   # Redraw 4 times per second
        screen=False,           # Don't take over the full terminal
        transient=False         # Keep the final display visible after capture ends
    )
