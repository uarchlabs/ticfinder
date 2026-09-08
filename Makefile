.PHONY: default

TIC=./tools/ticfinder.py
TIC_OPTS = --model en_core_web_md \
           --html reports

#--no-waivers
F1_WVR=--waiver-dir waivers
F1=README.md

default:
	rm -f reports/*
	$(TIC) $(TIC_OPTS) $(F1_WVR) $(F1)

F2_WVR=--waiver-dir private
F2=private/BLOG_bpu_14_directed_validation.md

f2:
	rm -f reports/*
	$(TIC) $(TIC_OPTS) $(F2_WVR) $(F2)

