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

"""Defines a pipeline to create a banner from the longest word in the input."""

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from my_package.my_transforms import  process_pdf
from my_package.utils.gcs_utils import list_pdfs_in_folder


def run_pipeline(input_folder: str, output_folder: str, processed_folder: str, pipeline_options_args: list[str]):
    """Defines and runs the Apache Beam pipeline."""
    beam_options = PipelineOptions(
        # temp_location=temp_location,
        # staging_location=staging_location,
        # project=project_id,
        pipeline_options_args
        # region="us-central1",  # Adjust the region if needed , not required for DirectRunner but required for DataflowRunner
        # runner="DirectRunner", # Use DirectRunner for local testing & DataflowRunner for GCP DF job
    )

    with beam.Pipeline(options=beam_options) as pipeline:
        (
            pipeline
            | "List Input Files" >> beam.Create(list_pdfs_in_folder(input_folder))
            | "Process PDFs" >> beam.Map(lambda blob_name: process_pdf(blob_name, input_folder, output_folder, processed_folder))
            | "Log Results" >> beam.io.WriteToText( output_folder + "myLog.txt")
        )
