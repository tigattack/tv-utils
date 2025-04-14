#!/usr/bin/env python3
"""
Convert XSPF playlist files to M3U format for SATIP/IPTV usage.
Optimized for DVB/SATIP channel lists.

Written entirely by AI as an experiment - Works On My Machine™
"""

import argparse
import html
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Channel:
    """Represents a channel in a SATIP/IPTV playlist"""

    title: str
    location: str
    number: str | None = None
    freq: str | None = None
    system: str | None = None
    params: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Extract frequency and system parameters from the location URL if available
        if self.location and "?" in self.location:
            self._parse_location_params()

    def _parse_location_params(self) -> None:
        """Parse parameters from location URL for SATIP channels"""
        # rtsp:///?freq=570&bw=8&tmode=8k&mtype=64qam&gi=132&fec=34&msys=dvbt&pids=0,16,17,18
        if "?" not in self.location:
            return

        query_string = self.location.split("?", 1)[1]
        for param in query_string.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                self.params[key] = value

                # Extract some useful parameters
                if key == "freq":
                    self.freq = value
                elif key == "msys":
                    self.system = value


class XSPFParser:
    """Parser for XSPF playlist files optimized for SATIP/IPTV channel lists"""

    XSPF_NAMESPACE = "{http://xspf.org/ns/0/}"

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.channels: list[Channel] = []

    def parse(self) -> list[Channel]:
        """Parse the XSPF file and extract all channels"""
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()

            # Process each track element (channel)
            track_elements = root.findall(f".//{self.XSPF_NAMESPACE}track")

            for track_elem in track_elements:
                # Extract basic track info
                title = self._get_element_text(track_elem, "title")
                location = self._get_element_text(track_elem, "location")
                track_num = self._get_element_text(track_elem, "trackNum")

                # Clean up the values
                title = title or f"Channel {track_num or 'Unknown'}"
                location = self._clean_location(location)

                if location:
                    self.channels.append(
                        Channel(title=title, location=location, number=track_num)
                    )

            return self.channels

        except ET.ParseError as e:
            print(f"Error parsing XSPF file: {e}", file=sys.stderr)
            return []

    def _get_element_text(self, parent: ET.Element, tag: str) -> str | None:
        """Extract text from an XML element with namespace support"""
        element = parent.find(f"{self.XSPF_NAMESPACE}{tag}")
        return element.text if element is not None and element.text else None

    def _clean_location(self, location: str | None) -> str:
        """Clean up location URLs, handling HTML entities"""
        if not location:
            return ""

        # Use html module to properly decode HTML entities
        return html.unescape(location)


class M3UWriter:
    """Writer for M3U playlist files with SATIP/IPTV specific features"""

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def write(self, channels: list[Channel], rtsp_server: str | None = None) -> None:
        """Write channels to an M3U file

        Args:
            channels: The list of channels to write
            rtsp_server: Optional RTSP server to insert in URLs if they're missing a server
        """
        try:
            with open(self.file_path, "w", encoding="utf-8") as m3u_file:
                # Write M3U header
                m3u_file.write("#EXTM3U\n")

                # Process URLs if rtsp_server is provided
                channels_with_server_count = 0

                # Write each channel
                for channel in channels:
                    if channel.location:
                        # Fix RTSP URL if needed
                        location = channel.location
                        if rtsp_server and location.startswith("rtsp:///"):
                            location = f"rtsp://{rtsp_server}/{location[8:]}"
                            channels_with_server_count += 1

                        # Write EXTINF line with channel info (without group-title)
                        m3u_file.write(f"#EXTINF:-1, {channel.title}\n")
                        m3u_file.write(f"{location}\n")

                output_msg = (
                    f"Successfully wrote {len(channels)} channels to {self.file_path}"
                )
                if rtsp_server and channels_with_server_count > 0:
                    output_msg += f" (Added server '{rtsp_server}' to {channels_with_server_count} channels)"

                print(output_msg)

        except IOError as e:
            print(f"Error writing M3U file: {e}", file=sys.stderr)


def process_conversion(
    input_path: Path,
    output_path: Path,
    dedup: bool = False,
    sort: bool = False,
    rtsp_server: str | None = None,
) -> bool:
    """Process the conversion from XSPF to M3U"""
    # Validate the input file exists
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' does not exist.", file=sys.stderr)
        return False

    # Parse the XSPF file
    parser = XSPFParser(input_path)
    channels = parser.parse()

    if not channels:
        print("No channels found in the XSPF file or parsing failed.", file=sys.stderr)
        return False

    # Sort channels by number if requested
    if sort:

        def channel_sort_key(channel: Channel) -> tuple[float, str]:
            # Try to convert channel number to int, or use a high value if not possible
            try:
                num = int(channel.number) if channel.number else float("inf")
                return (num, channel.title)
            except ValueError:
                return (float("inf"), channel.title)

        channels.sort(key=channel_sort_key)

    # Remove duplicate channels if requested
    if dedup:
        unique_channels: list[Channel] = []
        titles_seen: set[str] = set()

        for channel in channels:
            # Create a key based on title (removing frequency info if it exists)
            title_key = re.sub(r"\s+\d+\.\d+\s*MHz$", "", channel.title).strip()

            if title_key not in titles_seen:
                titles_seen.add(title_key)
                unique_channels.append(channel)

        channels = unique_channels

    # Write the M3U file
    writer = M3UWriter(output_path)
    writer.write(channels, rtsp_server=rtsp_server)

    return True


def main() -> None:
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(
        description="Convert XSPF playlist files to M3U format for SATIP/IPTV usage"
    )

    parser.add_argument("input_file", type=str, help="Path to the input XSPF file")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output M3U file (default: same name with .m3u extension)",
    )

    parser.add_argument(
        "-d",
        "--dedup",
        action="store_true",
        help="Remove duplicate channels with the same title",
    )

    parser.add_argument(
        "-s", "--sort", action="store_true", help="Sort channels by track number"
    )

    parser.add_argument(
        "-r",
        "--rtsp-server",
        type=str,
        help="RTSP server to insert in URLs if they're missing a server",
    )

    args = parser.parse_args()

    # Handle input path
    input_path = Path(args.input_file)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix(".m3u")

    # Perform the conversion
    success = process_conversion(
        input_path,
        output_path,
        dedup=args.dedup,
        sort=args.sort,
        rtsp_server=args.rtsp_server,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
