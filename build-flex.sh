#!/bin/bash

# This will exit the script in case of any errors in specific steps without executing further steps
set -e
# Set Variables
echo "********** Setting up variables... **********"
export PROJECT="your-project-id"
export BUCKET="your-bucket-name"
export REGION="us-central1"

###############
# Check if the bucket exists
if gsutil ls gs://$BUCKET 2>/dev/null; then
  echo "Bucket $BUCKET already exists. Proceeding..."
else
  echo "********** Creating Bucket... **********"
  gsutil mb -p $PROJECT gs://$BUCKET
  echo "********** Bucket created successfully with name $BUCKET **********"
fi

# Check if the repository exists
if gcloud artifacts repositories describe $REPOSITORY --location=$REGION --project=$PROJECT 2>/dev/null; then
  echo "Repository $REPOSITORY already exists. Proceeding..."
else
  echo "********** Creating Repository... **********"
  gcloud artifacts repositories create $REPOSITORY \
      --repository-format=docker \
      --location=$REGION \
      --project $PROJECT
  echo "********** Repository $REPOSITORY created successfully **********"
fi

echo "********** Bucket and Repository checks complete. Proceeding with further steps... **********"
###############

gcloud auth configure-docker $REGION-docker.pkg.dev

# Create base Container image
# Use a unique tag to version the artifacts that are built.
echo "********** Creating base container image... **********"

export TAG=`date +%Y%m%d-%H%M%S`
export SDK_CONTAINER_IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPOSITORY/my_rag_base_image:$TAG"

gcloud builds submit . --tag $SDK_CONTAINER_IMAGE --project $PROJECT

echo "********** Base container image created successfully $SDK_CONTAINER_IMAGE **********"

# Create Flex Template
echo "********** Creating Flex Template... **********"

export TEMPLATE_FILE=gs://$BUCKET/template/rag_data_processing-$TAG.json

# Make sure metadata.json file lcoation is correct for you
gcloud dataflow flex-template build $TEMPLATE_FILE  \
    --image $SDK_CONTAINER_IMAGE \
    --sdk-language "PYTHON" \
    --metadata-file=metadata.json \
    --project $PROJECT

echo "********** Flex Template created successfully at $TEMPLATE_FILE **********"

# Create Data flow job using the Flex template
gcloud dataflow flex-template run "rag-flex-`date +%Y%m%d-%H%M%S`" \
    --template-file-gcs-location $TEMPLATE_FILE \
    --region $REGION \
    --staging-location "gs://$BUCKET/staging" \
    --parameters sdk_container_image=$SDK_CONTAINER_IMAGE \
    --project $PROJECT \
    --parameters inputFolder="gs://$BUCKET/input/" \
    --parameters outputFolder="gs://$BUCKET/output/" \
    --parameters processedFolder="gs://$BUCKET/processed/"