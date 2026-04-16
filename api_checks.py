"""
Mobius Resource Management API
Covers: Tenant approval, Domain creation, Node creation, CIN (data) posting
"""

import requests
from typing import Optional


# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────

BASE_URL = "http://localhost:7601"  # Change to actual API base URL if different

# System-level JWT (for admin operations: approve, domain, node creation)
SYSTEM_JWT_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJzdWIiOiIwIiwidGVuYW50X2lkIjpudWxsLCJyb2xlIjoic3lzdGVtX3VzZXJfbWFuYWdlciIsImV4cCI6MTgzNjA1ODA2NX0"
    ".UeDKHYs0XyiUknZpdPtkAc79j7-Zu3RLTuCApWBH-5Y"
)

# API token used for CIN (data posting)
NODE_API_TOKEN = "9b94f6ac0530ade32290df7c5861aea6"


def _jwt_headers() -> dict:
    """Headers for system-level JWT authenticated requests."""
    return {
        "accept": "application/json",
        "Authorization": f"Bearer {SYSTEM_JWT_TOKEN}",
        "Content-Type": "application/json",
    }


def _node_headers() -> dict:
    """Headers for node-level API token requests (CIN posting)."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {NODE_API_TOKEN}",
    }


# ─────────────────────────────────────────────
# 1. Approve Tenant Request
# ─────────────────────────────────────────────

def approve_tenant_request(
    request_id: int,
    tenancy_mode: str = "shared",
    notes: str = "",
    server_ip: str = "192.168.1.100",
    server_password: str = "secure_password123",
    server_port: int = 5432,
) -> dict:
    """
    Approve a pending tenant registration request.

    Args:
        request_id:      ID of the tenant request to approve.
        tenancy_mode:    'shared' or 'dedicated'.
        notes:           Approval notes / reason.
        server_ip:       Database server IP assigned to the tenant.
        server_password: Database server password.
        server_port:     Database server port (default 5432 for PostgreSQL).

    Returns:
        Parsed JSON response from the API.
    """
    url = f"{BASE_URL}/api/v1/user_management/requests/{request_id}/approve-async"

    payload = {
        "tenancy_mode": tenancy_mode,
        "notes": notes,
        "server_ip": server_ip,
        "server_password": server_password,
        "server_port": server_port,
    }

    response = requests.post(url, json=payload, headers=_jwt_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────────────────
# 2. Create Domain
# ─────────────────────────────────────────────

def create_domain(
    name: str,
    short_name: str,
    description: str,
    parameter_name: list[str],
    data_types: list[str],
    accuracy: list[str],
    units: list[str],
    resolution: list[str],
    param_description: list[str],
    ideal: list[dict],
    moderate: list[dict],
    extreme: list[dict],
    is_active: bool = True,
) -> dict:
    """
    Create a new domain (sensor category) with parameter metadata.

    Each list argument (parameter_name, data_types, …) must have the same
    length — one entry per parameter belonging to this domain.

    Range dicts use the form: {"min": <float>, "max": <float>}

    Example
    -------
    create_domain(
        name="Air Quality",
        short_name="AQ",
        description="Outdoor air quality sensors",
        parameter_name=["Temperature", "Humidity"],
        data_types=["float", "float"],
        accuracy=["±0.5°C", "±2%"],
        units=["°C", "%RH"],
        resolution=["0.1", "0.1"],
        param_description=["Ambient temperature", "Relative humidity"],
        ideal=[{"min": 18, "max": 26}, {"min": 40, "max": 60}],
        moderate=[{"min": 10, "max": 35}, {"min": 30, "max": 70}],
        extreme=[{"min": 0, "max": 45},  {"min": 20, "max": 90}],
    )
    """
    url = f"{BASE_URL}/api/v1/resources/domains"

    payload = {
        "name": name,
        "short_name": short_name,
        "description": description,
        "parameter_name": parameter_name,
        "data_types": data_types,
        "accuracy": accuracy,
        "units": units,
        "resolution": resolution,
        "param_description": param_description,
        "ideal": ideal,
        "moderate": moderate,
        "extreme": extreme,
        "is_active": is_active,
    }

    response = requests.post(url, json=payload, headers=_jwt_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────────────────
# 3. Create Nodes (Bulk)
# ─────────────────────────────────────────────

def _build_node(
    name: str,
    area: str,
    domain_id: int,
    sensortype_id: int,
    ip: str,
    port: int,
    protocol: str,
    lat: float,
    long: float,
    frequency: str = "HOURLY",
    topic: Optional[str] = None,
) -> dict:
    """Build a single node dict for the bulk payload."""
    node = {
        "name": name,
        "area": area,
        "domain_id": domain_id,
        "sensortype_id": sensortype_id,
        "ip": ip,
        "port": port,
        "protocol": protocol,
        "lat": lat,
        "long": long,
        "frequency": frequency,
    }
    if topic:
        node["topic"] = topic
    return node


def create_nodes_bulk(nodes: list[dict]) -> dict:
    """
    Create multiple nodes in a single request.

    Args:
        nodes: List of node dicts. Use _build_node() to construct each entry,
               or supply raw dicts with the required keys.

    Required keys per node:
        name, area, domain_id, sensortype_id, ip, port, protocol, lat, long

    Optional keys:
        frequency (default "HOURLY"), topic (required for MQTT nodes)

    Example
    -------
    nodes = [
        _build_node(
            name="24_21_node1", area="test_area_1",
            domain_id=24, sensortype_id=21,
            ip="192.168.1.100", port=8080, protocol="HTTP",
            lat=17.4456, long=78.6567,
        ),
        _build_node(
            name="24_21_node2", area="test_area_2",
            domain_id=24, sensortype_id=21,
            ip="192.168.1.101", port=1883, protocol="MQTT",
            lat=17.4556, long=78.6667,
            topic="req/oneM2M/#",
        ),
    ]
    result = create_nodes_bulk(nodes)
    """
    url = f"{BASE_URL}/api/v1/resources/nodes/bulk"
    payload = {"nodes": nodes}

    response = requests.post(url, json=payload, headers=_jwt_headers(), timeout=30)
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────────────────
# 4. Post Sensor Data (CIN Creation)
# ─────────────────────────────────────────────

def post_sensor_data(node_id: int, data: dict) -> dict:
    """
    Post sensor readings to a specific node (creates a Content Instance / CIN).

    Args:
        node_id: ID of the target node.
        data:    Key-value pairs of sensor parameter name → reading value.
                 Keys must match the parameter names registered for the domain.

    Example
    -------
    post_sensor_data(
        node_id=3,
        data={
            "SE2 Air Temperature": 26.5,
            "SE2 Relative Humidity": 55,
            "SE2 CO2 Level": 650,
            "SE2 PM2.5": 35.2,
            "SE2 PM10": 48.7,
            "SE2 Noise Level": 62.3,
            "SE2 Light Intensity": 850,
            "SE2 Air Pressure": 1012,
            "SE2 VOC Level": 120,
            "SE2 AQI": 85,
        },
    )
    """
    url = f"{BASE_URL}/api/v1/resources/nodes/create-cin/{node_id}"

    response = requests.post(url, json=data, headers=_node_headers(), timeout=10)
    response.raise_for_status()
    return response.json()


# ─────────────────────────────────────────────
# Quick demo / smoke-test
# ─────────────────────────────────────────────

if __name__ == "__main__":

    # ── 1. Approve tenant request ──────────────────────────────────────────
    print("=== 1. Approving tenant request ===")
    try:
        result = approve_tenant_request(
            request_id=2,
            tenancy_mode="shared",
            notes="Approved for Case 1 - shared tenancy",
            server_ip="192.168.1.100",
            server_password="secure_password123",
            server_port=5432,
        )
        print("✅ Tenant approved:", result)
    except requests.HTTPError as e:
        print("❌ HTTP error:", e.response.status_code, e.response.text)
    except Exception as e:
        print("❌ Request failed:", e)

    # ── 2. Create domain ───────────────────────────────────────────────────
    print("\n=== 2. Creating domain ===")
    try:
        result = create_domain(
            name="Indoor Environment",
            short_name="IE",
            description="Indoor air quality and environment monitoring",
            parameter_name=[
                "Air Temperature", "Relative Humidity", "CO2 Level",
                "PM2.5", "PM10", "Noise Level",
                "Light Intensity", "Air Pressure", "VOC Level", "AQI",
            ],
            data_types=["float"] * 10,
            accuracy=["±0.5°C", "±2%", "±30ppm", "±5μg", "±5μg",
                      "±1dB", "±5lx", "±0.5hPa", "±5ppb", "±5"],
            units=["°C", "%RH", "ppm", "μg/m³", "μg/m³",
                   "dB", "lx", "hPa", "ppb", "AQI"],
            resolution=["0.1", "0.1", "1", "0.1", "0.1",
                        "0.1", "1", "0.1", "1", "1"],
            param_description=[
                "Ambient air temperature", "Relative humidity level",
                "Carbon dioxide concentration", "Fine particulate matter (PM2.5)",
                "Coarse particulate matter (PM10)", "Ambient noise level",
                "Light intensity", "Atmospheric pressure",
                "Volatile organic compounds", "Air Quality Index",
            ],
            ideal=[
                {"min": 20, "max": 26}, {"min": 40, "max": 60},
                {"min": 400, "max": 800}, {"min": 0, "max": 12},
                {"min": 0, "max": 20},  {"min": 0, "max": 50},
                {"min": 300, "max": 500}, {"min": 1010, "max": 1020},
                {"min": 0, "max": 200}, {"min": 0, "max": 50},
            ],
            moderate=[
                {"min": 15, "max": 30}, {"min": 30, "max": 70},
                {"min": 800, "max": 1500}, {"min": 12, "max": 35},
                {"min": 20, "max": 50},  {"min": 50, "max": 70},
                {"min": 100, "max": 750}, {"min": 1000, "max": 1025},
                {"min": 200, "max": 500}, {"min": 50, "max": 100},
            ],
            extreme=[
                {"min": 0, "max": 40},  {"min": 10, "max": 90},
                {"min": 1500, "max": 5000}, {"min": 35, "max": 150},
                {"min": 50, "max": 250},  {"min": 70, "max": 120},
                {"min": 0, "max": 1000}, {"min": 980, "max": 1040},
                {"min": 500, "max": 2000}, {"min": 100, "max": 300},
            ],
        )
        print("✅ Domain created:", result)
    except requests.HTTPError as e:
        print("❌ HTTP error:", e.response.status_code, e.response.text)
    except Exception as e:
        print("❌ Request failed:", e)

    # ── 3. Create nodes (bulk) ─────────────────────────────────────────────
    print("\n=== 3. Creating nodes (bulk) ===")
    try:
        nodes = [
            _build_node(
                name="24_21_node1", area="test_area_1",
                domain_id=24, sensortype_id=21,
                ip="192.168.1.100", port=8080, protocol="HTTP",
                lat=17.4456, long=78.6567,
            ),
            _build_node(
                name="24_21_node2", area="test_area_2",
                domain_id=24, sensortype_id=21,
                ip="192.168.1.101", port=1883, protocol="MQTT",
                lat=17.4556, long=78.6667,
                topic="req/oneM2M/#",
            ),
        ]
        result = create_nodes_bulk(nodes)
        print("✅ Nodes created:", result)
    except requests.HTTPError as e:
        print("❌ HTTP error:", e.response.status_code, e.response.text)
    except Exception as e:
        print("❌ Request failed:", e)

    # ── 4. Post sensor data (CIN) ──────────────────────────────────────────
    print("\n=== 4. Posting sensor data (CIN) ===")
    try:
        result = post_sensor_data(
            node_id=3,
            data={
                "SE2 Air Temperature": 26.5,
                "SE2 Relative Humidity": 55,
                "SE2 CO2 Level": 650,
                "SE2 PM2.5": 35.2,
                "SE2 PM10": 48.7,
                "SE2 Noise Level": 62.3,
                "SE2 Light Intensity": 850,
                "SE2 Air Pressure": 1012,
                "SE2 VOC Level": 120,
                "SE2 AQI": 85,
            },
        )
        print("✅ Sensor data posted:", result)
    except requests.HTTPError as e:
        print("❌ HTTP error:", e.response.status_code, e.response.text)
    except Exception as e:
        print("❌ Request failed:", e)