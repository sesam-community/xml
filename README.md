# XML parser and renderer

Supports parsing and rendering of XML files.

## Example System Config
```
{
  "_id": "xml-converter",
  "type": "system:microservice",
  "docker": {
    "image": "sesamcommunity/xml:latest",
    "port": 5000
  }
},
{
  "_id": "my-ssh-server",
  "type": "system:microservice",
  "docker": {
    "image": "sesamcommunity/sshfs:latest",
    [..]
    "port": 5000
  }
}
```

## Parsing XML
```
{
  "_id": "my-xml-source",
  "type": "pipe",
  "source": {
    "type": "json",
    "system": "xml-converter",
    "url": "/?url=http://my-ssh-server:5000/some-input-file.xml&xml_path=customerRecords.customerRecord&updated_path=system.customerChangeDateTime&since=2001-12-17T09:30:47%2B02:00",
  "transform": {
    "type": "dtl",
    "rules": {
      "default": [
        ["add", "_id","path.to.id"],
        ["copy", "*"]
      ]
    }
  }
}
```
It supports updated path if it exists, if not; remove updated_path and since from url.

```
<html>
<bar>Hei</bar>
</html>
```

will be converted to

```
[
  {
    "html": {
      "bar": "Hello"
    }
  }
]

```

## Rendering XML
```
{
  "_id": "my-xml-sink",
  "type": "pipe",
  "source": {
    "type": "dataset",
    "dataset": "some_dataset"
  },
  "sink": {
    "type": "json",
    "system": "xml-converter",
    "url": "/?url=http://my-ssh-server:5000/some-output-file.xml"
  }
}
```

```
  {
    "html": {
      "bar": "Hello"
    }
  }
```

will be rendered as

```
<html>
<bar>Hei</bar>
</html>
```
