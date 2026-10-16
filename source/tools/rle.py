import sys,re
def rle(s):
    out=[];i=0;n=len(s)
    while i<n:
        best=None
        for p in range(1,9):
            pat=s[i:i+p]
            if len(pat)<p: break
            k=1
            while s[i+k*p:i+(k+1)*p]==pat: k+=1
            saved=k*p-(len(pat)+len(str(k))+3)
            if k>=3 and saved>4 and (best is None or saved>best[2]): best=(pat,k,saved)
        if best:
            out.append('!%s*%d!'%(best[0],best[1])); i+=len(best[0])*best[1]
        else:
            out.append(s[i]); i+=1
    return ''.join(out)
def ck(s):
    h=0
    for ch in s: h=(h*31+ord(ch))%1000003
    return h
name=sys.argv[1]; size=int(sys.argv[2]) if len(sys.argv)>2 else 900
s=open(name).read().strip()
chunks=[s[i:i+size] for i in range(0,len(s),size)]
print('TOTAL',len(s),'CHUNKS',len(chunks))
for c in chunks: print(len(c), ck(c), rle(c))
