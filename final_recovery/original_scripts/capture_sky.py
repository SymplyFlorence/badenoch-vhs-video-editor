import os,json,urllib.request,urllib.error
from pathlib import Path
from playwright.sync_api import sync_playwright
b=Path('/workspace/badenoch-revision-preflight/evidence')
url='https://news.sky.com/story/robert-jenrick-sacked-from-tory-shadow-cabinet-for-plotting-to-defect-13494578'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'],proxy={'server':os.environ['HTTPS_PROXY']})
 page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=4,java_script_enabled=False)
 def verified_fetch(route):
  req=route.request
  if req.method not in ['GET','HEAD']:
   route.abort();return
  try:
   headers={k:v for k,v in req.headers.items() if k.lower() not in ['accept-encoding','host','connection']}
   with urllib.request.urlopen(urllib.request.Request(req.url,headers=headers,method=req.method),timeout=20) as r:
    body=r.read(12000000)
    response_headers={k:v for k,v in r.headers.items() if k.lower() not in ['content-encoding','transfer-encoding','content-length','connection']}
    route.fulfill(status=r.status,headers=response_headers,body=body)
  except Exception:
   route.abort()
 page.route('**/*',verified_fetch)
 page.goto(url,wait_until='domcontentloaded',timeout=120000)
 page.wait_for_timeout(2000)
 print('Title:',page.title(),flush=True)
 page.screenshot(path=str(b/'sky-headline.png'))
 page.locator('.sdc-article-header').first.screenshot(path=str(b/'sky-article-header.png'))
 page.locator('img.sdc-site-header-logo-light').first.screenshot(path=str(b/'sky-logo.png'))
 loc=page.locator('p').filter(has_text='I was presented with clear, irrefutable evidence').first
 print('Quote count:',loc.count(),flush=True)
 loc.scroll_into_view_if_needed()
 loc.screenshot(path=str(b/'sky-statement-paragraph.png'))
 dismissal=page.locator('p').filter(has_text='I have sacked Robert Jenrick from the shadow cabinet').first
 dismissal.scroll_into_view_if_needed()
 dismissal.screenshot(path=str(b/'sky-dismissal-paragraph.png'))
 page.screenshot(path=str(b/'sky-statement-context.png'))
 # Save exact browser text geometry for highlights in cropped source screenshots.
 def geometry(locator,phrases):
  return locator.evaluate("""(el, phrases) => {
   const box=el.getBoundingClientRect();
   const walker=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let ns=[];let node;
   while(node=walker.nextNode())ns.push(node);
   let text=ns.map(n=>n.textContent).join('');
   const spans={};
   for(const p of phrases){const start=text.indexOf(p);if(start<0)continue;let total=0;let a,b,ao,bo;
    for(const n of ns){const end=total+n.textContent.length;if(a===undefined&&start<end){a=n;ao=start-total;}if(start+p.length<=end){b=n;bo=start+p.length-total;break;}total=end;}
    const r=document.createRange();r.setStart(a,ao);r.setEnd(b,bo);spans[p]=Array.from(r.getClientRects()).map(x=>({x:(x.x-box.x)*4,y:(x.y-box.y)*4,width:x.width*4,height:x.height*4}));}
   return {text,width:box.width*4,height:box.height*4,spans};
  }""",phrases)
 g={'statement':geometry(loc,['clear, irrefutable evidence','plotting in secret to defect']), 'dismissal':geometry(dismissal,['sacked Robert Jenrick from the shadow cabinet','removed the whip','suspended his party membership with immediate effect'])}
 (b/'article_geometry.json').write_text(json.dumps(g,indent=2))
 print(json.dumps(g),flush=True)
 browser.close()
