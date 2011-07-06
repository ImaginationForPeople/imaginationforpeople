#!/usr/bin/env python
import os
os.system("django-lint --rcfile pylint.rc apps > report.lint")
print "DONE."
