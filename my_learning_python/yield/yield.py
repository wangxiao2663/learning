def f():
    print "Before first yield"
    yield 1
    print "Before second yield"
    yield 2
    print "After third yield"
 
g = f()
print "Before first next"
g.next()
print "Before second next"
g.next()
print "Before third yield"
g.next()