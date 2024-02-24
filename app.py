import assemblyai as aai #https://www.assemblyai.com/pricing
import openai #https://platform.openai.com/api-keys
import elevenlabs #https://elevenlabs.io/projects
from queue import Queue

aai.settings.api_key="API_KEY" 
openai.api_key="API_KEY"
elevenlabs.set_api_key("API_KEY")

transcript_queue=Queue()

def on_data(transcript:aai.RealtimeTranscript):
    if not transcript.text:
        return
    if isinstance(transcript,aai.RealtimeFinalTranscript):
        transcript_queue.put(transcript.text+'')
        print("User: ", transcript.text,end="\r\n")
    else:
        print(transcript.text,end="\r")
    
def on_error(error:aai.RealtimeError):
    print("An Error Occured: ", error)

#conversation loop
def handle_conversation():
    while True:
        transcriber=aai.RealtimeTranscriber(
            on_data=on_data,
            on_error=on_error,
            sample_rate=44_100,
        )

        #Start the Connection
        transcriber.connect()

        #Open the Micro phone Realtech Stream
        microphone_stream=aai.extras.MicrophoneStream()

        #Stream audio from the microphone
        transcriber.stream(microphone_stream)

        #Close Current Transcription session with Ctrl+c
        transcriber.close()

        #Retrieve data from queue
        transcript_result=transcript_queue.get()

        #Send the transcript to OpenAI for Response generation
        response=openai.ChatCompleteion.create(
            model='gpt-4',
            messages=[
                {"role":"system","content":'You are a higly skilled AI, answer the question given within a maximum of 500 characters'},
                {"role":"user","content":transcript_result}
            ]
        )

        text=response['choices'][0]['message']['content']

        #Generate Audio from text that we created
        #audio=elevenlabs.generate(
        #    text=text,
        #    voice="Bella"
        #)
        #print("\nAI:", text,end="\r\n")
        
        #elevenlabs.play(audio)

handle_conversation()