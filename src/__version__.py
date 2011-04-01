from helixcore.buildutils.git import comments_num

major = 1
minor = 0
stage = 1 # 0 - alpha, 1 - beta, 2 - release candidate, 3 - release
patch = comments_num('.')

version = '%s.%s.%s-%s' % (major, minor, stage, patch)