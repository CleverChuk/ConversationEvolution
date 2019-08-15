import sys
sys.path.append("C:\\Users\\chubi\\Documents\\REU\\ConversationEvolution\\www\\src\\mapper")
import api.mapper as mp
from api.models import TreeNode

tm = mp.TreeMapper()
a = TreeNode('a')
b = TreeNode('b', type='comment')
b['parent_id'] = 'a'
b['s'] = 'p'

c = TreeNode('c',  type='comment')
c['parent_id'] = 'a'
c['s'] = 'n'

d = TreeNode('d',  type='comment')
d['parent_id'] = 'a'
d['s'] = 'p'

e = TreeNode('e', type='comment')
e['parent_id'] = 'b'
e['s'] = 'p'

f = TreeNode('f',  type='comment')
f['parent_id'] = 'c'
f['s'] = 'p'

g = TreeNode('g', type='comment')
g['parent_id'] = 'c'
g['s'] = 'n'

h = TreeNode('h',  type='comment')
h['parent_id'] = 'd'
h['s'] = 'n'

i = TreeNode('i',  type='comment')
i['parent_id'] = 'f'
i['s'] = 'n'

a["children"].extend([b,c,d])
b.addChild(e)

c["children"].extend([f,g])
d.addChild(h)
f.addChild(i)

tm.execute(a, 2, lambda n: n['s'])
# print(tm._generateIntervals(28,7))
print(tm.intervals)
print(tm.cluster)





