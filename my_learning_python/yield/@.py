def spamrun(fn):
    def sayspam(*args):
        print "spam,spam,spam"
    return sayspam
@spamrun
def useful(a,b):
    print a**2+b**2
   
useful(3,4)


def addspam(fn):
    def new(*args):
        print "spam,spam,spam"
        return fn(*args)
    return new
@addspam
def useful(a,b):
    print a**2+b**2
   
useful(4,3)



def decorator(fn):
    def test(*args):
        print "My god!"*3
        return fn(*args)
    return test
@decorator
def other(a,b):
    print a**2+b**2

if __name__=="__main__":
    other(4,3)
    other(3,4)
