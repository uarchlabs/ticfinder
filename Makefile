.PHONY: default f2 notes regress

TIC=./tools/ticfinder.py
TIC_OPTS = --model en_core_web_md \
           --html reports

#--no-waivers
WVR=--waiver-dir waivers

F1=README.md

default:
	rm -f reports/*
	$(TIC) $(TIC_OPTS) $(WVR) $(F1)

F2=$(shell realpath --relative-to=. "$(PACINO)")/blogs/BLOG_bpu_14_directed_validation.md

f2:
	@test -n "$(PACINO)" || { echo "PACINO is not set; run . tools/setup.sh"; exit 1; }
	rm -f reports/*
	$(TIC) $(TIC_OPTS) $(WVR) $(F2)

NOTES=$(wildcard notes/*.md)

notes:
	rm -f reports/*
	$(TIC) $(TIC_OPTS) $(WVR) $(NOTES)

regress:
	./tools/tests.py
