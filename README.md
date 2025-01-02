# RAG Dataflow Flex Template: a pipeline with dependencies and a custom container image

This sample project illustrates the following Dataflow Python pipeline setup:

-   The pipeline is a package that consists of
    [multiple files](https://beam.apache.org/documentation/sdks/python-pipeline-dependencies/#multiple-file-dependencies).

-   The pipeline has at least one dependency that is not provided in the default
    Dataflow runtime environment.

-   The workflow uses a
    [custom container image](https://cloud.google.com/dataflow/docs/guides/using-custom-containers)
    to preinstall dependencies and to define the pipeline runtime environment.

-   The workflow uses a
    [Dataflow Flex Template](https://cloud.google.com/dataflow/docs/concepts/dataflow-templates)
    to control the pipeline submission environment.

-   The runtime and submission environment use same set of Python dependencies
    and can be created in a reproducible manner.

## What it does exactly?

To illustrate this setup, we use a pipeline that does the following:

1.  List PDFs from input folder of google Storage bucket

1.  Create embeddings using text-embedding-004 model from google Vertex AI

1.  Store embeddings in pickle file in output folder of storage bucket

1. Move processed pdf files to processed folder of storage bucket

## The structure of the repository

The pipeline package is comprised of the `src/my_package` directory, the
`pyproject.toml` file and the `setup.py` file. The package defines the pipeline,
the pipeline dependencies, and the input parameters. You can define multiple
pipelines in the same package. The `my_package.launcher` module is used to
submit the pipeline to a runner.

The `main.py` file provides a top-level entrypoint to trigger the pipeline
launcher from a launch environment.

The `Dockerfile` defines the runtime environment for the pipeline. It also
configures the Flex Template, which lets you reuse the runtime image to build
the Flex Template.

The `requirements.txt` file defines all Python packages in the dependency chain
of the pipeline package. Use it to create reproducible Python environments in
the Docker image.

The `metadata.json` file defines Flex Template parameters and their validation
rules. It is optional.

## Before you begin

1.  Make sure to enable Dataflow API & other ralated API like Cloud Build. Refer Dataflow documentation for details.

1.  Clone the [`rag-data-pipeline` repository](https://github.com/kameshpoc/rag-data-pipeline)
    and navigate to the code sample.

    ```sh
    git clone https://github.com/kameshpoc/rag-data-pipeline
    ```

## Create a Cloud Storage bucket

```sh
export PROJECT="project-id"
export BUCKET="your-bucket"
export REGION="us-central1"
gsutil mb -p $PROJECT gs://$BUCKET
```

## Create an Artifact Registry repository

```sh
export REPOSITORY="your-repository"

gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --project $PROJECT

gcloud auth configure-docker $REGION-docker.pkg.dev
```

## Build a Docker image for the pipeline runtime environment

Using a
[custom SDK container image](https://cloud.google.com/dataflow/docs/guides/using-custom-containers)
allows flexible customizations of the runtime environment.

This example uses the custom container image both to preinstall all of the
pipeline dependencies before job submission and to create a reproducible runtime
environment.

To illustrate customizations, a
[custom base base image](https://cloud.google.com/dataflow/docs/guides/build-container-image#use_a_custom_base_image)
is used to build the SDK container image.

The Flex Template launcher is included in the SDK container image, which makes
it possible to
[use the SDK container image to build a Flex Template](https://cloud.google.com/dataflow/docs/guides/templates/configuring-flex-templates#use_custom_container_images).

```sh
# Use a unique tag to version the artifacts that are built.
export TAG=`date +%Y%m%d-%H%M%S`
export SDK_CONTAINER_IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPOSITORY/my_rag_base_image:$TAG"

gcloud builds submit . --tag $SDK_CONTAINER_IMAGE --project $PROJECT
```

## Build the Flex Template

Build the Flex Template
[from the SDK container image](https://cloud.google.com/dataflow/docs/guides/templates/configuring-flex-templates#use_custom_container_images).
Using the runtime image as the Flex Template image reduces the number of Docker
images that need to be maintained. It also ensures that the pipeline uses the
same dependencies at submission and at runtime.

```sh
export TEMPLATE_FILE=gs://$BUCKET/rag-data-processing-$TAG.json
```

```sh
gcloud dataflow flex-template build $TEMPLATE_FILE  \
    --image $SDK_CONTAINER_IMAGE \
    --sdk-language "PYTHON" \
    --metadata-file=metadata.json \
    --project $PROJECT
```

## Run the template

This will create a dataflow job

```sh
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
```
Alternatively use below bash file for executng all of the above commands. Don't forget to make it executable
```bash
chmod +x ./build-flex.sh
```
To run bash file use below. Before running the file, make sure to update file with your specific input details.
```bash
./build-flex.sh
```

After the pipeline finishes, use the following command to inspect the output:

```bash
gsutil cat gs://$BUCKET/output*
```

## Optional: Update the dependencies in the requirements file and rebuild the Docker images

The top-level pipeline dependencies are defined in the `dependencies` section of
the `pyproject.toml` file.

The `requirements.txt` file pins all Python dependencies, that must be installed
in the Docker container image, including the transitive dependencies. Listing
all packages produces reproducible Python environments every time the image is
built. Version control the `requirements.txt` file together with the rest of
pipeline code.

When the dependencies of your pipeline change or when you want to use the latest
available versions of packages in the pipeline's dependency chain, regenerate
the `requirements.txt` file:

  ```bash
  python3 -m pip install pip-tools
  python3 -m piptools compile -o requirements.txt pyproject.toml
  ```

If you base your custom container image on the standard Apache Beam base image,
to reduce the image size and to give preference to the versions already
installed in the Apache Beam base image, use a constraints file:

```bash
wget https://raw.githubusercontent.com/apache/beam/release-2.54.0/sdks/python/container/py311/base_image_requirements.txt
python3 -m piptools compile --constraint=base_image_requirements.txt ./pyproject.toml
```

Alternatively, take the following steps:

1.  Use an empty `requirements.txt` file.
1.  Build the SDK container Docker image from the Docker file.
1.  Collect the output of `pip freeze` at the last stage of the Docker build.
1.  Seed the `requirements.txt` file with that content.

For more information, see the Apache Beam
[reproducible environments](https://beam.apache.org/documentation/sdks/python-pipeline-dependencies/#create-reproducible-environments)
documentation.

---
## Repository: rag-data-pipeline

This repository is public for reference purposes only. Contributions in the form of issues, pull requests, or feature requests are not accepted. If you'd like to use or modify this project, please fork it.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENCE) file for details.
