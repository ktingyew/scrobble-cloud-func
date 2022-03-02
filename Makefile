deploy.zip: $(shell find src/*.py -type f) main.py requirements.txt
	zip -FSr deploy.zip ./ \
		-x .\* \
		-x \*__pycache__\* \
		-x \*.env \
		-x Makefile 
