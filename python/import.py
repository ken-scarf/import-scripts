import requests
import sys
import os
import gzip
import json
from itertools import islice

scarf_name = os.environ.get("SCARF_NAME", "defaultname")
scarf_token = os.environ.get("SCARF_AUTH_TOKEN", "defaulttoken")


def is_gzipped(data: bytes) -> bool:
    # checks the gzip magic number 1F8B08
    return data.startswith(b"\x1f\x8b")


headers = {"Authorization": f"Bearer {scarf_token}"}


# get my artifacts
def get_tracking_pixel_ids():
    tracking_pixel_url = f"https://api.scarf.sh/v2/tracking-pixels/{scarf_name}"
    headers["Content-Type"] = "application/json"
    response = requests.get(tracking_pixel_url, headers=headers).json()
    results = response["results"]
    return list(map(lambda result: result["id"], results))


def get_package_ids():
    tracking_pixel_url = f"https://api.scarf.sh/v2/packages/{scarf_name}"
    headers["Content-Type"] = "application/json"
    response = requests.get(tracking_pixel_url, headers=headers).json()
    results = response["results"]
    return list(map(lambda result: result["id"], results))


tracking_pixel_ids = set(get_tracking_pixel_ids())
package_ids = set(get_package_ids())


def validate_compressed_input(stream=sys.stdin.buffer):
    peek_data = stream.peek(2)
    if is_gzipped(peek_data):
        with gzip.open(stream, "rt") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if "$package" in data:
                        package_id = data["$package"]
                        if package_id in package_ids:
                            yield data
                        else:
                            print(f"Unknown artifact id: {package_id}", file=sys.stderr)

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}", file=sys.stderr)
    else:
        for line in stream:
            try:
                data = json.loads(line.decode("utf-8").strip())
                yield data
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}", file=sys.stderr)


buffer = []


def import_event(data, batch_size=10000):
    headers["Content-Type"] = "application/x-ndjson"
    headers["Content-Encoding"] = "gzip"
    stringified_json_line = json.dumps(data)

    buffer.append(stringified_json_line)

    if len(buffer) >= batch_size:
        ndjson_line = "\n".join(buffer)
        compressed_data = gzip.compress(ndjson_line.encode("utf-8"))

        response = requests.post(
            url=f"https://api.scarf.sh/v2/{scarf_name}/import",
            data=compressed_data,
            headers=headers,
        )
        print(response.text)

        buffer.clear()


def flush_buffer():
    headers["Content-Type"] = "application/x-ndjson"
    headers["Content-Encoding"] = "gzip"
    if buffer:
        ndjson_line = "\n".join(buffer)
        compressed_data = gzip.compress(ndjson_line.encode("utf-8"))

        response = requests.post(
            url=f"https://api.scarf.sh/v2/{scarf_name}/import",
            data=compressed_data,
            headers=headers,
        )
        buffer.clear()

    print("Remaining batch processed")


def main():
    for data in validate_compressed_input():
        import_event(data)
    flush_buffer()


if __name__ == "__main__":
    main()
