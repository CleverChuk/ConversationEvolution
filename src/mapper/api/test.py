import sys

sys.path.append("C:\\Users\\chubi\\Documents\\REU\\ConversationEvolution\\www\\src\\mapper")
import api.mapper as mp
from api.models import TreeNode

tm = mp.TreeMapper()
root = TreeNode('a')
b = TreeNode('b', type='comment')
b['parent_id'] = 'a'
b['sentiment'] = 'positive'

c = TreeNode('c', type='comment')
c['parent_id'] = 'a'
c['sentiment'] = 'negative'

d = TreeNode('d', type='comment')
d['parent_id'] = 'a'
d['sentiment'] = 'positive'

e = TreeNode('e', type='comment')
e['parent_id'] = 'b'
e['sentiment'] = 'positive'

f = TreeNode('f', type='comment')
f['parent_id'] = 'c'
f['sentiment'] = 'positive'

g = TreeNode('g', type='comment')
g['parent_id'] = 'c'
g['sentiment'] = 'negative'

h = TreeNode('h', type='comment')
h['parent_id'] = 'd'
h['sentiment'] = 'negative'

i = TreeNode('i', type='comment')
i['parent_id'] = 'f'
i['sentiment'] = 'negative'

root["children"].extend([b, c, d])
b.add_child(e)

c["children"].extend([f, g])
d.add_child(h)
f.add_child(i)

# tm.execute(root, 2, lambda n: n['sentiment'])
# print(tm._generateIntervals(28,7))
# print(tm.intervals)
# print(tm.cluster)
