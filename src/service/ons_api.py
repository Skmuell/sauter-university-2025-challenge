import http.client
import json

def get_ons_metadata(package_id: str) -> dict:
    conn = http.client.HTTPSConnection("dados.ons.org.br")

    headers = {
        "Accept": "*/*",
        "User-Agent": "Python Client"
    }

    conn.request(
        "GET",
        f"/api/3/action/package_show?id={package_id}",
        headers=headers
    )

    response = conn.getresponse()
    result = response.read()
    conn.close()

    if not result or result.strip() == b"":
        return {"error": "Empty response from API"}

    try:
        data = json.loads(result.decode("utf-8"))
        if not data:
            return {"error": "Empty JSON response"}
        return data
    except json.JSONDecodeError:
        return {"error": "Invalid JSON", "raw": result.decode("utf-8")}

def get_resource_ids(package_id: str) -> list[dict]:
    data = get_ons_metadata(package_id)

    if "error" in data:
        return []

    resources = data.get("result", {}).get("resources", [])

    parquets = [
        {"id": item["id"], "name": item["name"]}
        for item in resources
        if item.get("format", "").upper() == "PARQUET"
    ]

    return parquets

