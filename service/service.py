import json
import xmltodict

from flask import Flask, request, Response
import os
import requests

import logger
from dotdictify import Dotdictify

app = Flask(__name__)

logger = logger.Logger('xml')

class XmlParser:
    def __init__(self, args):
        self._xml_path = args.get("xml_path")
        self._updated_path = args.get("updated_path")
        self._since = args.get("since")

    def parse(self, stream):
        root_element = xmltodict.parse(stream)

        if self._xml_path is not None:

            if isinstance(list(Dotdictify(root_element).get(self._xml_path))[0], dict):
                l = list(Dotdictify(root_element).get(self._xml_path))
            else:
                l = [Dotdictify(root_element).get(self._xml_path)]
        else:
            l = [root_element]
        if self._updated_path is not None:
            for entity in l:
                b = Dotdictify(entity)
                entity["_updated"] = b.get(self._updated_path)
        if self._since is not None:
            logger.info("Fetching data since: %s" % self._since)
            return list(filter(l, self._since))
        return l

    def filter(l, since):
        for e in l:
            if e.get("_updated") > since:
                yield e


@app.route("/", methods=["GET"])
def get():
    parser = XmlParser(request.args)
    url = request.args["url"]
    xml = requests.get(url).text
    return Response(response=json.dumps(parser.parse(xml)), mimetype='application/json')


@app.route('/', methods=["POST"])
def post():
    url = request.args["url"]
    xml = xmltodict.unparse(request.get_json(), pretty=True, full_document=False).encode('utf-8')
    r = requests.post(url, xml)
    if r.status_code != 200:
        return Response(response=r.text, status=r.status_code)
    else:
        return Response(response="Great Success!")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
