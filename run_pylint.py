#!/usr/bin/env python
import os
os.system("django-lint --disable=E1102 --rcfile pylint.rc apps > report.lint")
print "DONE."
