# this file will be the code that runs on the zero to await requests made by
# the website & apply for & then resolve those prompts
# should display a loading screen while waiting for an image
# and after the first prompted image is displayed, fade between the generated variants
# do so until the screen is touched or X time passes
# should be at an intro screen of some kind while awaiting a new prompt
import requests, os, pygame, firebase_admin, openai
from firebase_admin import credentials
from firebase_admin import db


# firebase config
config = {
    apiKey: "AIzaSyBa7WNFwugtTqRwm8hqMsMgeExmRX_tEpw",
    authDomain: "just-another-future.firebaseapp.com",
    databaseURL: 'https://just-another-future-default-rtdb.asia-southeast1.firebasedatabase.app',
    projectId: "just-another-future",
    storageBucket: "just-another-future.appspot.com",
    messagingSenderId: "1001702454477",
    appId: "1:1001702454477:web:8068c9f2f39ded3bb76584",
    measurementId: "G-XEE5RNJMHF"
}

# Fetch the service account key JSON file contents
cred = credentials.Certificate('just-another-future-firebase-adminsdk-1x2xw-8e2b5e3b5f.json')

# Initialize the app with a service account, granting admin privileges & the other config info
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://just-another-future-default-rtdb.asia-southeast1.firebasedatabase.app'
})

# create an images folder if it doesn't already exist in this directory
if not os.path.exists('images'):
    os.makedirs('images')

# function to update the pi zero's connection status
def updateConnectionStatus(status):
    ref = db.reference('connections/pi-zero')
    ref.set({
        'connected': status
    })

# function to update the awaiting prompt status
def updateAwaitingPrompt(status):
    ref = db.reference('futurePrompts/awaitingNewPrompt')
    ref.set({
        'awaiting': status
    })

# function to get the current prompt from the database
def getCurPrompt():
    ref = db.reference('futurePrompts/curPrompt')
    return ref.get()

# defining the core callback function that triggers when the pi zero
# gets a new prompt via a change in the database's curPrompt value
def onCurPromptChange():
    # update the awaiting prompt status to false
    updateAwaitingPrompt(False)
    # get the current prompt
    curPrompt = getCurPrompt()

    # create a subfolder for the current prompt if it doesn't already exist within the images folder
    sanatizedPrompt = curPrompt.replace(' ', '_') # we sanatize to avoid issues with directory names
    sanatizedPrompt = ''.join(e for e in sanatizedPrompt if e.isalnum() or e == '-')
    if not os.path.exists('images/' + sanatizedPrompt):
        os.makedirs('images/' + sanatizedPrompt)
        # we also want a subfolder for variants of the image
        os.makedirs('images/' + sanatizedPrompt + '/variants')

    # query the openai dalle api for the prompt to get a generated image
    # and save the image to the subfolder for the current prompt
    # we'll use the prompt as the image name
    response = openai.Image.create(
        prompt = curPrompt,
        n = 1,
        size = "1024x1024"
    )
    image_url = response['data'][0]['url']
    # download the image to the subfolder for the current prompt
    r = requests.get(image_url, allow_redirects=True)
    open('images/' + sanatizedPrompt + '/' + curPrompt + '.jpg', 'wb').write(r.content)


# when the script begins, update the pi zero's connection status to true
updateConnectionStatus(True)

# setup a listener for the curPrompt value in the database
curPromptRef = db.reference('/futurePrompts/curPrompt/')
curPromptRef.listen(onCurPromptChange())

# TODO: make sure the listener gets closed when the script ends & refractor as needed for response times
# we also should double check line 82 to see if the curPrompt used might cause name issues
