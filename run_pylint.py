#!/usr/bin/env python
import os
os.system("django-lint apps > report.lint")
print "DONE."
