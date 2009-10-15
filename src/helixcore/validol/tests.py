#@PydevCodeAnalysisIgnore
import cProfile

if __name__ == "__main__":
    import doctest
    import validol
    print 'testing...'
    doctest.testmod(validol)
    print 'done'
#
#    for _ in range(3):
#        cProfile.run("""
#for _ in range(500000):
#    validol.validate_list([str], ['foo'])
#""")
