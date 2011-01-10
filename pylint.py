#!/usr/bin/env python
import os
os.system("pylint --disable=E1102 --rcfile pylint.rc apps > report.lint")
print "DONE."
