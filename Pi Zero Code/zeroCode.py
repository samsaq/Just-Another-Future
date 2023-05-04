# this file will be the code that runs on the zero to await requests made by
# the website & apply for & then resolve those prompts
# should display a loading screen while waiting for an image
# and after the first prompted image is displayed, fade between the generated variants
# do so until the screen is touched or X time passes
# should be at an intro screen of some kind while awaiting a new prompt
import requests, os, pygame, firebase_admin, openai, time, sys
from firebase_admin import credentials
from firebase_admin import db

debug = False
numVariants = 2 # number of variants to generate for each prompt

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Change to the script directory
os.chdir(current_dir)

# firebase config
configFirebase = {
    "apiKey": "AIzaSyBa7WNFwugtTqRwm8hqMsMgeExmRX_tEpw",
    "authDomain": "just-another-future.firebaseapp.com",
    "databaseURL": 'https://just-another-future-default-rtdb.asia-southeast1.firebasedatabase.app',
    "projectId": "just-another-future",
    "storageBucket": "just-another-future.appspot.com",
    "messagingSenderId": "1001702454477",
    "appId": "1:1001702454477:web:8068c9f2f39ded3bb76584",
    "measurementId": "G-XEE5RNJMHF"
}

# pygame initializations
pygame.init()

# Set up the Pygame window and the clock
if debug:
    screen = pygame.display.set_mode((800, 600))
else:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# set openai key, read in from openaiKey.txt
openaiKeyFile = open('openaiKey.txt', 'r')
openai.api_key = openaiKeyFile.read()
openaiKeyFile.close()

# Fetch the service account key JSON file contents
cred = credentials.Certificate('just-another-future-firebase-adminsdk-vy89h-b2ad978410.json')

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
    global awaitingPrompt
    awaitingPrompt = status
    ref = db.reference('futurePrompts/awaitingNewPrompt')
    ref.set({
        'awaiting': status
    })

# function to get the current prompt from the database
def getCurPrompt():
    ref = db.reference('futurePrompts/curPrompt')
    return ref.get()

# loading screen function
def displayLoading(screen):
    # Define the loading screen message and font
    loadingMessage = "Loading..."
    loadingFont = pygame.font.Font(None, 36)

    # Create a surface for the loading screen
    loadingScreen = pygame.Surface(screen.get_size())
    loadingScreen = loadingScreen.convert()
    loadingScreen.fill((0, 0, 0))  # fill the screen with a black background

    # Display the loading message on the loading screen
    text = loadingFont.render(loadingMessage, 1, (255, 255, 255)) # white loading text
    textPos = text.get_rect(centerx=loadingScreen.get_width()/2,
                              centery=loadingScreen.get_height()/2)
    loadingScreen.blit(text, textPos)

    # Display the loading screen on the main window
    screen.blit(loadingScreen, (0, 0))
    pygame.display.flip()

# function to use already generated images to display on the pi zero & transition
def displayArt():
    # We'll stay on each image for 4 seconds, then fade to the next one
    # After 2 loops, we'll go back to the intro screen
    sanatizedPrompt = curPrompt.replace(' ', '_') # we sanatize to avoid issues with directory names
    sanatizedPrompt = ''.join(e for e in sanatizedPrompt if e.isalnum() or e == '-')

    # get the relevant images
    promptImage = pygame.image.load('images/' + sanatizedPrompt + '/promptImage.jpg')
    variantsArray = [] # array of variant image surfaces
    for i in range (numVariants):
        variantPath = 'images/' + sanatizedPrompt + '/variants/' + 'variant' + str(i) + '.jpg'
        variantsArray.append(pygame.image.load(variantPath))
    
    # Display the prompt image on the main window with a transition from the previous loading screen
    currentScreen = pygame.display.get_surface()
    transitionImages(screen, currentScreen, promptImage)
    time.sleep(4)

    # now do the loop for the variants
    for i in range (len(variantsArray)):
        # Display the variant image on the main window with a transition from the previous image
        currentScreen = pygame.display.get_surface()
        transitionImages(screen, currentScreen, variantsArray[i])

        # wait 4 seconds
        time.sleep(4)


# function to display the intro screen where the pi zero awaits a new prompt
def displayIntro():
    # Define the intro screen message and font
    introMessage = "Imagine the future..."
    introFont = pygame.font.Font(None, 36)

    # Create a surface for the intro screen
    introScreen = pygame.Surface(screen.get_size())
    introScreen = introScreen.convert()
    introScreen.fill((255, 255, 255))  # fill the screen with a white background (to serve as backlight)

    # Display the intro message on the intro screen
    text = introFont.render(introMessage, 1, (0, 0, 0)) # black intro text
    textPos = text.get_rect(centerx=introScreen.get_width()/2,
                              centery=introScreen.get_height()/2)
    introScreen.blit(text, textPos)

    # Display the intro screen on the main window
    screen.blit(introScreen, (0, 0))
    pygame.display.flip()

# function to transition with a fade effect from the current to the next image
def transitionImages(screen, currentImage, targetImage, fadeTime=1.0, fadeStep=0.02):
    # Set up the timer
    fadeAlpha = 0.0  # current alpha value for the fade effect
    fadeStartTime = time.time()  # time when the fade started

    # Run the transition loop
    while True:
        # Calculate the current alpha value based on the elapsed time and fade time
        elapsedTime = time.time() - fadeStartTime
        if elapsedTime >= fadeTime:
            # End of fade effect, switch to new image
            currentImage = targetImage
            break
        else:
            # Fade effect in progress, calculate new alpha value
            fadeAlpha += fadeStep
            current_alpha = int(255 * (1 - fadeAlpha))
            newAlpha = int(255 * fadeAlpha)

        # Set the alpha value for the current image
        currentImage = currentImage.copy()
        currentImage.set_alpha(current_alpha)

        # Draw the new image over the current image with gradually increasing alpha value
        newImage = targetImage.copy()
        newImage.set_alpha(newAlpha)
        screen.blit(currentImage, (0, 0))
        screen.blit(newImage, (0, 0))

        # Display the current image on the game window
        pygame.display.update()

        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    # Display the final image on the game window
    screen.blit(currentImage, (0, 0))
    pygame.display.update()

# defining the core callback function that triggers when the pi zero
# gets a new prompt via a change in the database's curPrompt value
def onCurPromptChange(event):
    # get the current prompt
    global curPrompt
    curPrompt = event.data
    # update the awaiting prompt status to false
    updateAwaitingPrompt(False)

# function to load images from the openai dalle api
# will block until the images are loaded
def loadImages():
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

    displayLoading(screen)

    response = openai.Image.create(
        prompt = curPrompt,
        n = 1,
        size = "1024x1024"
    )
    image_url = response['data'][0]['url']
    # download the image to the subfolder for the current prompt
    r = requests.get(image_url, allow_redirects=True)
    imagePath = 'images/' + sanatizedPrompt + '/' + 'promptImage' + '.jpg'
    with open(imagePath, 'wb') as f:
        f.write(r.content)
        f.close()

    # now to get the variants of the image (8 of them, for now)
    variants = openai.Image.create_variation(
        # based off of the current prompt image
        image = open('images/' + sanatizedPrompt + '/' + 'promptImage' + '.jpg', 'rb'),
        n=numVariants,
        size = "1024x1024"
    )
    # use the urls to download the images to the variants subfolder
    for i in range(numVariants):
        variant_url = variants['data'][i]['url']
        variantPath = 'images/' + sanatizedPrompt + '/variants/' + 'variant' + str(i) + '.jpg'
        r = requests.get(variant_url, allow_redirects=True)
        with open(variantPath, 'wb') as f:
            f.write(r.content)
            f.close()

    # loop to wait for the images to finish downloading
    numExpectedImages = numVariants + 1  # plus the prompt image
    numImagesDownloaded = 0
    while numImagesDownloaded < numExpectedImages:
        numImagesDownloaded = len(os.listdir('images/' + sanatizedPrompt + '/variants'))
        numImagesDownloaded += 1  # to account for the prompt image
        if numImagesDownloaded < numExpectedImages:
            # wait for a bit before checking again
            time.sleep(0.5)

# setup a listener for the curPrompt value in the database
curPromptRef = db.reference('/futurePrompts/curPrompt/')
curPromptRef.listen(onCurPromptChange)

currentState = 'intro'  # starting state of the state machine
updateConnectionStatus(True)  # update the connection status to true
curPrompt = getCurPrompt()
awaitingPrompt = True  # flag to indicate if we're waiting for a new prompt for the state machine

# Start the Pygame event loop to handle events and update the display
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    # state machine to handle the different screens
    if currentState == 'intro':
        displayIntro()
        updateAwaitingPrompt(True) # updates the database and the global variable
        # we can use the global to check if the current prompt has been updated
        if(awaitingPrompt == False): # awaitingPrompt is updated by the listener
            currentState = 'loading'
            loadImages()
            currentScreen = pygame.display.get_surface()
            displayArt()
            updateAwaitingPrompt(True)
            currentState = 'intro'

    # Limit the frame rate to 60 fps
    clock.tick(60)

# Quit Pygame and exit the program
updateConnectionStatus(False)  # update the connection status to false
updateAwaitingPrompt(True)
pygame.quit()