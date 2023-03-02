import shutil
from tempfile import SpooledTemporaryFile

import requests


def download_from_url(url) -> SpooledTemporaryFile:
    with SpooledTemporaryFile(mode='wb+') as file:
        response = requests.get(url, stream=True)
        shutil.copyfileobj(response.raw, file)
        del response
        file.seek(0)
        return file
