import base64
import glob
import gzip
import json
import os


def decode(value, decompress=False):
    """Decodes response from Base64 encoded string."""
    decoded = base64.b64decode(value)
    if decompress:
        decoded = gzip.decompress(decoded)
    return json.loads(decoded.decode())


def encode(value, compress=False):
    """Converts dict to JSON and encodes it to Base64."""
    encoded = json.dumps(value, separators=(",", ":")).encode()
    if compress:
        encoded = gzip.compress(encoded)
    return base64.b64encode(encoded).decode()


def replace_real_credentials(cassette_dir, production_token, header, test_token):
    cassettes = glob.glob(os.path.join(cassette_dir, "*.json"))
    for cassette_path in cassettes:
        with open(cassette_path) as fp:
            data = json.load(fp)
        rewrite_required = False
        for record in data["http_interactions"]:
            if record["request"]["headers"].get(header) == [production_token]:
                record["request"]["headers"][header] = [test_token]
                rewrite_required = True
        if rewrite_required:
            with open(cassette_path, "w") as fp:
                json.dump(data, fp, sort_keys=True, indent=2, separators=(",", ": "))
