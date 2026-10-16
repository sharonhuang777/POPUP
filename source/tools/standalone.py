import os as _os
S = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), 'demo') + '/'
s=open(S+'Popup Demo.html').read()
head='''<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Popup">
<meta name="theme-color" content="#FCF1E8">
'''
s=s.replace('<meta charset="utf-8">\n','',1)
i=s.index('</style>')+len('</style>')
_os.makedirs(S+'standalone', exist_ok=True)
open(S+'standalone/index.html','w').write(head+s[:i]+'\n</head><body>\n'+s[i:]+'\n</body></html>\n')
