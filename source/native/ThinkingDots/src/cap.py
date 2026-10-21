import asyncio,sys
from playwright.async_api import async_playwright
from PIL import Image
async def cap(name,n,fps=30):
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':120,'height':120})
        await pg.goto(f'file:///tmp/claude-0/-home-claude/c4e0787a-0c45-5649-94d5-ee8c831d9d2e/scratchpad/webp/{name}.html'); await pg.wait_for_timeout(300)
        fr=[]
        for i in range(n):
            await pg.evaluate(f"document.getAnimations().forEach(a=>{{a.pause();a.currentTime={i*1000/fps}}})")
            await pg.screenshot(path='t.png',omit_background=True); fr.append(Image.open('t.png').convert('RGBA'))
        await b.close(); return fr
async def main():
    lp=await cap('loop',69)        # 2.3 s orbit = seamless
    mg=await cap('merge',72)       # 1 s orbit + 1.1 s merge + 0.3 s hold
    for nm,fr,loop in [('thinking_dots_loop',lp,0),('thinking_dots_merge_once',mg,1)]:
        fr[0].save(nm+'.webp',save_all=True,append_images=fr[1:],duration=round(1000/30),loop=loop,lossless=True,method=6)
        fr[0].save(nm+'_lossy.webp',save_all=True,append_images=fr[1:],duration=round(1000/30),loop=loop,quality=85,method=6,alpha_quality=100)
asyncio.run(main())
