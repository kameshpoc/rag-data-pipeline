# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Defines command line arguments for the pipeline defined in the package."""

import argparse

# from my_package import my_pipeline
from my_package import my_pipeline

def run(argv: list[str] | None = None):
    """Parses the parameters provided on the command line and runs the pipeline."""
    parser = argparse.ArgumentParser(description="Run RAG Data Processing Pipeline")
    parser.add_argument("--inputFolder", required=True, help="Path to the input folder in GCS")
    parser.add_argument("--outputFolder", required=True, help="Path to the output folder in GCS")
    parser.add_argument("--processedFolder", required=True, help="Path to the processed folder in GCS")
    # parser.add_argument("--tempLocation", required=True, help="Path to the temporary location in GCS")
    # parser.add_argument("--stagingLocation", required=True, help="Path to the staging location in GCS")
    # parser.add_argument("--projectID", required=True, help="Google Cloud Project ID") 
    pipeline_args, other_args = parser.parse_known_args(argv)

    my_pipeline.run_pipeline(
        pipeline_args.inputFolder,
        pipeline_args.outputFolder, 
        pipeline_args.processedFolder,
        other_args
    )

    # pipeline.run()
