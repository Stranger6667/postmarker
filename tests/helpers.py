# coding: utf-8
import base64
import glob
import json
import os


def decode(value):
    """
    Decodes response from Base64 encoded string.
    """
    return json.loads(base64.b64decode(value).decode())


def encode(value):
    """
    Converts dict to JSON and encodes it to Base64.
    """
    return base64.b64encode(json.dumps(value, separators=(',', ':')).encode())


def replace_real_credentials(cassette_dir, production_token, test_token):
    cassettes = glob.glob(os.path.join(cassette_dir, '*.json'))
    for cassette_path in cassettes:
        with open(cassette_path) as fp:
            data = json.load(fp)
        rewrite_required = False
        for record in data['http_interactions']:
            if record['request']['headers'].get('X-Postmark-Server-Token') == [production_token]:
                record['request']['headers']['X-Postmark-Server-Token'] = [test_token]
                rewrite_required = True
        if rewrite_required:
            with open(cassette_path, 'w') as fp:
                json.dump(data, fp, sort_keys=True, indent=2, separators=(',', ': '))
