import concurrent.futures,urllib.request,urllib.error,json
from pathlib import Path
base=Path('/workspace/badenoch-revision-preflight/evidence');base.mkdir(exist_ok=True)
urls={
'sky.html':'https://news.sky.com/story/robert-jenrick-sacked-from-tory-shadow-cabinet-for-plotting-to-defect-13494578',
'official_results.pdf':'https://researchbriefings.files.parliament.uk/documents/SN01366/SN01366.pdf',
'itv.html':'https://www.itv.com/news/2026-01-15/robert-jenrick-sacked-over-alleged-plot-to-defect-from-tories-badenoch-says',
'commons_search.json':'https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=Robert%20Jenrick%20Nigel%20Farage&gsrnamespace=6&gsrlimit=10&prop=imageinfo&iiprop=url%7Cextmetadata&format=json'
}
def fetch(item):
 name,url=item
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'DocumentaryResearch/1.0 (source verification and attribution)'})
  with urllib.request.urlopen(req,timeout=40) as r:
   data=r.read(20000000);(base/name).write_bytes(data);return name,r.status,r.headers.get('Content-Type'),len(data)
 except Exception as e:return name,str(e)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:
 for r in p.map(fetch,urls.items()):print(r,flush=True)
