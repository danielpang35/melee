"""Execute one connector-provided upload request; never invent destinations."""
import sys,json,urllib.parse,http.client,uuid,mimetypes
from pathlib import Path
kind,request_path,file_path=sys.argv[1:]
spec=json.loads(Path(request_path).read_text(encoding='utf-8'))
file=Path(file_path);data=file.read_bytes()
if kind=='linear':
    r=spec['uploadRequest'];url=r['url'];headers=r['headers'];method='PUT';body=data
    if isinstance(headers,list):headers={h['key']:h['value'] for h in headers}
else:
    url=spec['upload_url'];headers=spec.get('upload_headers',{});method='POST'
    boundary='CharacterReview'+uuid.uuid4().hex
    prefix=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{file.name}"\r\nContent-Type: {mimetypes.guess_type(file.name)[0]}\r\n\r\n').encode()
    body=prefix+data+f'\r\n--{boundary}--\r\n'.encode()
    headers['Content-Type']='multipart/form-data; boundary='+boundary
parts=urllib.parse.urlsplit(url)
if parts.scheme!='https':raise RuntimeError('Expected connector HTTPS upload URL')
c=http.client.HTTPSConnection(parts.netloc,timeout=50)
c.putrequest(method,parts.path+('?' +parts.query if parts.query else ''),skip_accept_encoding=True)
for k,v in headers.items():c.putheader(k,str(v))
if not any(k.lower()=='content-length' for k in headers):c.putheader('Content-Length',str(len(body)))
c.endheaders(body);r=c.getresponse();payload=r.read()
if not 200<=r.status<300:raise RuntimeError(str(r.status)+' '+payload.decode(errors='replace')[:500])
print(json.dumps({'status':r.status,'response':payload.decode(errors='replace')}))
