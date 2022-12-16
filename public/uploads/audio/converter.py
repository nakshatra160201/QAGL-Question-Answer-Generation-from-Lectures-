import sys
import os
from docx2pdf import convert
path = "C:/Users/Sneha devrani/Desktop/Capstone/qagl/public/uploads/audio/"
import azure.cognitiveservices.speech as speechsdk
import torch
import json
import transformers
from transformers import BartTokenizer, BartForConditionalGeneration
#taking video,blob updation
import moviepy.editor as mp
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import logging
import sys
import requests
import time
import swagger_client as cris_client
import aspose.words as aw
transformers.utils.move_cache()
# path=str(os.getcwd())

# lol =str( path.replace("\\",'/'))
# path=path.replace("\","/")
# print(lol+'/loda.docx')
# convert(path+sys.argv[1])
# print("jhbgbhn")
# import os
# import pathlib

# file_path = str(pathlib.Path('.').absolute() / 'loda.docx')
# fp=file_path.split('\\')
# print(fp)
# fnl=""
# for i in range(0, len(fp)):
#     if i!=0:
#         fnl+='/'
#     fnl+=fp[i]
# print(fnl)
# # file_path = os.path.join(os.getcwd(), 'loda.docx')
# # print(file_path)

# convert(fnl) 
clip = mp.VideoFileClip(path+sys.argv[1])
clip.audio.write_audiofile(path+"index1.mp3")

connect_str="DefaultEndpointsProtocol=https;AccountName=audiosaspn;AccountKey=AtwKsyMGqAUHQRpGrWUnDW2xJqofITfHeAQMhnPz+WwxEthtFHKFUgG+x2JRe7xHkK+UgI0Put6A+AStiWo0bQ=="
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_name = 'uploads'
local_file_name="index1.mp3"
upload_file_path = os.path.join(r'C:/Users/Sneha devrani/Desktop/Capstone/qagl/public/uploads/audio', local_file_name)
blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)
with open(upload_file_path, "rb") as data:
    blob_client.upload_blob(data)


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
        format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")

# Your subscription key and region for the speech service
SUBSCRIPTION_KEY = "3cea74bf345945eab084943b7c0a724c"
SERVICE_REGION = "centralindia"

NAME = "Simple transcription"
DESCRIPTION = "Simple transcription description"

LOCALE = "en-US"
RECORDINGS_BLOB_URI = "https://audiosaspn.blob.core.windows.net/uploads/index1.mp3"

# Provide the uri of a container with audio files for transcribing all of them
# with a single request. At least 'read' and 'list' (rl) permissions are required.
# RECORDINGS_CONTAINER_URI = "<Your SAS Uri to a container of audio files>"

# Set model information when doing transcription with custom models
MODEL_REFERENCE = None  # guid of a custom model


def transcribe_from_single_blob(uri, properties):
    """
    Transcribe a single audio file located at `uri` using the settings specified in `properties`
    using the base model for the specified locale.
    """
    transcription_definition = cris_client.Transcription(
        display_name=NAME,
        description=DESCRIPTION,
        locale=LOCALE,
        content_urls=[uri],
        properties=properties
    )

    return transcription_definition


def transcribe_with_custom_model(api, uri, properties):
    """
    Transcribe a single audio file located at `uri` using the settings specified in `properties`
    using the base model for the specified locale.
    """
    # Model information (ADAPTED_ACOUSTIC_ID and ADAPTED_LANGUAGE_ID) must be set above.
    if MODEL_REFERENCE is None:
        logging.error("Custom model ids must be set when using custom models")
        sys.exit()

    model = api.get_model(MODEL_REFERENCE)

    transcription_definition = cris_client.Transcription(
        display_name=NAME,
        description=DESCRIPTION,
        locale=LOCALE,
        content_urls=[uri],
        model=model,
        properties=properties
    )

    return transcription_definition


def transcribe_from_container(uri, properties):
    """
    Transcribe all files in the container located at `uri` using the settings specified in `properties`
    using the base model for the specified locale.
    """
    transcription_definition = cris_client.Transcription(
        display_name=NAME,
        description=DESCRIPTION,
        locale=LOCALE,
        content_container_url=uri,
        properties=properties
    )

    return transcription_definition


def _paginate(api, paginated_object):
    """
    The autogenerated client does not support pagination. This function returns a generator over
    all items of the array that the paginated object `paginated_object` is part of.
    """
    yield from paginated_object.values
    typename = type(paginated_object)
    auth_settings = ["apiKeyHeader", "apiKeyQuery"]
    while paginated_object.next_link:
        link = paginated_object.next_link[len(api.api_client.configuration.host):]
        paginated_object, status, headers = api.api_client.call_api(link, "GET",
            response_type=typename, auth_settings=auth_settings)

        if status == 200:
            yield from paginated_object.values
        else:
            raise Exception(f"could not receive paginated data: status {status}")


def delete_all_transcriptions(api):
    """
    Delete all transcriptions associated with your speech resource.
    """
    logging.info("Deleting all existing completed transcriptions.")

    # get all transcriptions for the subscription
    transcriptions = list(_paginate(api, api.get_transcriptions()))

    # Delete all pre-existing completed transcriptions.
    # If transcriptions are still running or not started, they will not be deleted.
    for transcription in transcriptions:
        transcription_id = transcription._self.split('/')[-1]
        logging.debug(f"Deleting transcription with id {transcription_id}")
        try:
            api.delete_transcription(transcription_id)
        except cris_client.rest.ApiException as exc:
            logging.error(f"Could not delete transcription {transcription_id}: {exc}")


def transcribe():
    logging.info("Starting transcription client...")

    # configure API key authorization: subscription_key
    configuration = cris_client.Configuration()
    configuration.api_key["Ocp-Apim-Subscription-Key"] = SUBSCRIPTION_KEY
    configuration.host = f"https://{SERVICE_REGION}.api.cognitive.microsoft.com/speechtotext/v3.0"

    # create the client object and authenticate
    client = cris_client.ApiClient(configuration)

    # create an instance of the transcription api class
    api = cris_client.CustomSpeechTranscriptionsApi(api_client=client)

    # Specify transcription properties by passing a dict to the properties parameter. See
    # https://docs.microsoft.com/azure/cognitive-services/speech-service/batch-transcription#configuration-properties
    # for supported parameters.
    properties = {
        # "punctuationMode": "DictatedAndAutomatic",
        # "profanityFilterMode": "Masked",
        # "wordLevelTimestampsEnabled": True,
        # "diarizationEnabled": True,
        # "destinationContainerUrl": "<SAS Uri with at least write (w) permissions for an Azure Storage blob container that results should be written to>",
        # "timeToLive": "PT1H"
    }

    # Use base models for transcription. Comment this block if you are using a custom model.
    transcription_definition = transcribe_from_single_blob(RECORDINGS_BLOB_URI, properties)

    # Uncomment this block to use custom models for transcription.
    # transcription_definition = transcribe_with_custom_model(api, RECORDINGS_BLOB_URI, properties)

    # Uncomment this block to transcribe all files from a container.
    # transcription_definition = transcribe_from_container(RECORDINGS_CONTAINER_URI, properties)

    created_transcription, status, headers = api.create_transcription_with_http_info(transcription=transcription_definition)

    # get the transcription Id from the location URI
    transcription_id = headers["location"].split("/")[-1]

    # Log information about the created transcription. If you should ask for support, please
    # include this information.
    logging.info(f"Created new transcription with id '{transcription_id}' in region {SERVICE_REGION}")

    logging.info("Checking status.")

    completed = False

    while not completed:
        # wait for 5 seconds before refreshing the transcription status
        time.sleep(5)

        transcription = api.get_transcription(transcription_id)
#         abcd=transcription
        logging.info(f"Transcriptions status: {transcription.status}")

        if transcription.status in ("Failed", "Succeeded"):
            completed = True

        if transcription.status == "Succeeded":
            pag_files = api.get_transcription_files(transcription_id)
            for file_data in _paginate(api, pag_files):
                if file_data.kind != "Transcription":
                    continue

                audiofilename = file_data.name
                results_url = file_data.links.content_url
                results = requests.get(results_url)
                print(results.content.decode('utf-8'))
                return results.content.decode('utf-8')
#                 logging.info(f"Results for {audiofilename}:\n{results.content.decode('utf-8')}")
        elif transcription.status == "Failed":
            return "Error 404"



resy=transcribe()

ree=json.loads(resy)
transcribed_text=ree['combinedRecognizedPhrases'][0]['display']
doc = aw.Document()
builder = aw.DocumentBuilder(doc)
builder.write(transcribed_text)
doc.save(path+"summary.docx")


# tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
# model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

# torch_device = 'cpu'
# def bart_summarize(text, num_beams, length_penalty, max_length, min_length, no_repeat_ngram_size):
  
#   text = text.replace('\n','')
#   text_input_ids = tokenizer.batch_encode_plus([text], return_tensors='pt', max_length=1024)['input_ids'].to(torch_device)
#   summary_ids = model.generate(text_input_ids, num_beams=int(num_beams), length_penalty=float(length_penalty), max_length=int(max_length), min_length=int(min_length), no_repeat_ngram_size=int(no_repeat_ngram_size))           
#   summary_txt = tokenizer.decode(summary_ids.squeeze(), skip_special_tokens=True)
#   return summary_txt


# ans=bart_summarize(transcribed_text,4,2.0,1000,50,3)

# doc = aw.Document()
# doc1 = aw.Document()
# builder = aw.DocumentBuilder(doc)
# builder1 = aw.DocumentBuilder(doc1)
# builder.write(transcribed_text)
# builder1.write(ans)
# doc.save(path+"summary.docx")
# doc1.save(path+"summary1.docx")

convert(path+"summary.docx")