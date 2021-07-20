import json
import xmltodict
import yaml

from xml.parsers.expat import ExpatError
from flask import Flask, request, Response, jsonify
import os
import requests

import logger
from dotdictify import Dotdictify

app = Flask(__name__)

CONFIG = {
"default_encoding" : "utf-8"
}

##Helper function for yielding on batch fetch
def stream_json(entities):
    logger.info("streaming started")
    try:
        first = True
        yield '['
        for i, row in enumerate(entities):
            if not first:
                yield ','
            else:
                first = False          
            yield json.dumps(row)
        yield ']'
    except Exception as e:
        logger.error(f"Exiting with error : {e}")
    logger.info("stream ended")
##
 
logger = logger.Logger('xml')

class XmlParser:
    def __init__(self, args):
        self._xml_path = args.get("xml_path")
        self._updated_path = args.get("updated_path")
        self._since = args.get("since")

    def parse(self, stream):
        try:
            root_element = xmltodict.parse(stream)
        except ExpatError as e:
            logger.info(f"root element is failing with {e}")

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


@app.route("/file", methods=["GET"])
def get():
    parser = XmlParser(request.args)
    url = request.args["url"]
    xml = requests.get(url).content.decode('utf-8-sig')
    return Response(response=json.dumps(parser.parse(xml)), mimetype='application/json')


@app.route("/filebulk", methods=["GET"])
def get_folder():
    parser = XmlParser(request.args)
    url = request.args["url"]
    xml = requests.get(url).content.decode('utf-8-sig')
    xml_to_dict = yaml.load(xml)
    xml_content = []
    for xml_file in xml_to_dict['files']:
        try:
            parsed_xml = parser.parse(str(xml_file))
            xml_content.append(parsed_xml[0])
        except Exception as e:
            logger.info(f"Skipping xml file with error : {e}")

    logger.info("Finished runnig parse to write to sesam pipe...")
    return Response(stream_json(xml_content), mimetype='application/json')


@app.route('/', methods=["POST"])
def post():
    """
    Accepts and parses args.url, then sends new request to the given url param
    """
    url = request.args["url"]
    xml = xmltodict.unparse(request.get_json(), pretty=True, full_document=False).encode('utf-8')
    r = requests.post(url, xml)
    if r.status_code != 200:
        return Response(response=r.text, status=r.status_code)
    else:
        return Response(response="Great Success!")


@app.route('/json_string_to_xml_file', methods=["POST"])
def json_string_to_xml_file():
    """
    Accepts and parses args.url, then sends new request to the given url param
    """
    url = request.args["url"]
    xml = xmltodict.unparse(request.get_json(), pretty=True, full_document=False).encode('utf-8')
    r = requests.post(url, xml)
    if r.status_code != 200:
        return Response(response=r.text, status=r.status_code)
    else:
        return Response(response="Great Success!")

@app.route('/xml_string_to_json', methods=["POST"])
def xml_string_to_json():
    
    """
    - http request args: 
        xml_payload_node : what json key holds the xml string that needs convertion 
        xml_encoding : the encoding to use when parsing the xml data
    - accepts a application/json HTTP body
        sesam namespaces needs to be removed
    - xml attributes will be prefixed by "@" in the json data
    """
    
    xml_node = request.args["xml_payload_node"]
    xml_encoding = request.args["xml_payload_encoding"]
    
    if xml_encoding.strip() == "":
        xml_encoding = CONFIG["default_encoding"] 

    request_payload = request.get_json()

    try:
        data_dict = xmltodict.parse(request_payload[xml_node],encoding=xml_encoding, xml_attribs=True)
        json_data = json.dumps(data_dict)
    except Exception as ex:
        
        logger.error(ex)
        

    return Response(response=json_data, mimetype='application/json')
    

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
