.PHONY: deploy zip

zip: $(find ./src -iname "*.py" -type f) logging.ini main.py requirements.txt
# Make dir if exists
	mkdir -p ./Deployment
# Copy src over
	cp -r ./src ./Deployment
# Copy other files to target (-t) Deployment
	cp -t ./Deployment logging.ini main.py requirements.txt
# Make new subdir
	cd Deployment; mkdir -p ./zip
# zip all the files in ./Deployment, excluding (-x) the cache and egg
	cd Deployment; zip -FSr ./zip/scrobble_cloud.zip * \
		-x ./src/my_scrobble.egg-info \
		-x ./src/my_scrobble/__pycache__ \
		-x zip/

deploy:
	cd Deployment/zip; gcloud functions deploy scrobble-gcs-bq 


