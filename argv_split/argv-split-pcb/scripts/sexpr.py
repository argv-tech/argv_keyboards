"""Small KiCad S-expression reader/writer, preserving atom/string distinction."""
import re,json
class Atom(str): pass
def parse(s):
 tokens=iter(re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',s)); stack=[]; root=None
 for t in tokens:
  if t=='(':
   a=[]
   if stack: stack[-1].append(a)
   else: root=a
   stack.append(a)
  elif t==')': stack.pop()
  else: stack[-1].append(json.loads(t) if t.startswith('"') else Atom(t))
 return root
def dump(x,level=0):
 if not isinstance(x,list): return str(x) if isinstance(x,Atom) else json.dumps(x,ensure_ascii=False)
 if not any(isinstance(v,list) for v in x): return '('+' '.join(dump(v) for v in x)+')'
 return '('+' '.join(dump(v) for v in x[:next((i for i,v in enumerate(x) if isinstance(v,list)),len(x))])+''.join('\n'+'  '*(level+1)+dump(v,level+1) for v in x[next((i for i,v in enumerate(x) if isinstance(v,list)),len(x)):])+')'
def children(x,k): return [v for v in x if isinstance(v,list) and v and v[0]==k]
def one(x,k): return next(iter(children(x,k)),None)
