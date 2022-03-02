
# scrobble-cloud-func

This code reads from my last.fm scrobbles, then processes them, then uploads to BigQuery and Cloud Storage.

Since it uses [GCP](https://cloud.google.com/) resources, you need a service account that is authorised to access the aforementioned resources.

# Hosting

This code is designed to be hosted on [Cloud Functions](https://cloud.google.com/functions). 

Execute `make` on project root directory. It creates a file `deploy.zip`. This is the codebase that will be submitted to Cloud Functions. 

The file `sample.env` is a sample file to configure all the environment variables needed of this Function. 