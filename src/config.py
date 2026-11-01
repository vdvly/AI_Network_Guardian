"""Shared settings for the fixed network-traffic preparation pipeline."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"

RANDOM_STATE = 42
TEST_SIZE = 0.20
RAW_FILE = "network_traffic.csv"
RAW_PATH = DATA_RAW / RAW_FILE

TIME = "time"
SRC_IP = "source_ip_int"
DST_IP = "destination_ip_int"
SRC_PORT = "source_port"
DST_PORT = "destination_port"
PROTOCOL = "protocol"
DURATION = "duration"
PACKETS = "packet_count"
BYTES_SENT = "bytes_sent"
BYTES_RECEIVED = "bytes_received"
LABEL = "label"
BYTES_PER_PACKET = "bytes_per_packet"

NUMERIC_COLS = [DURATION, PACKETS, BYTES_SENT, BYTES_RECEIVED, BYTES_PER_PACKET]
SPLIT_STRATEGY = "stratified"
INCLUDE_IDENTIFIERS = False
PROTOCOL_CODE_MAP = None
