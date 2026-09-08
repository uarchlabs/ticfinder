

TIC=./tools/ticfinder.py
TIC_OPTS = --model en_core_web_md \
           --html reports \
           --waiver-dir waivers
#           --no-waivers



#FILE=BLOG_bpu_13_contradiction_detection.md
#FILE=../pacino/blogs/BLOG_bpu_14_directed_validation.md
FILE=README.md

default:
	rm -f reports/*
	$(TIC) $(TIC_OPTS) $(FILE)
