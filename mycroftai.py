import pyttsx3,json,traceback,re,datetime,pyaudio,os,threading#subprocess
from trafilatura import fetch_url, extract
from playsound import playsound
from pygame import mixer
from vosk import Model, KaldiRecognizer
from duckduckgo_search import DDGS
import modules

class VoiceAssistant():
    engine = pyttsx3.init()
    model = Model(r"vosk-model-en-us-0.42-gigaspeech")
    recognizer = KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio()
    stream =mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()
    #tts=""
    #inpt=0
    hinpt=False
    info=open("../config.json")
    info=json.loads(info.read())
    mixer.init()
    '''
    RAG:
    You are Alexa, an AI assitant, you are able to run functions in the next format:
    'run function nameofyourfunction argumentsifanyornone'
    example:
    run function weather "california"
    run function search "Who was the creator of computer science?"
    run function checkEmail "none"
    '''
    rag=["""
    You are an AI Assistant named Alex, who responds to the user with helpful information, tips, and jokes just like Jarvis from the marvel universe. You must be answer all the questions truthfully. You are trained in python function calling and you need to use these functions to answer the user's questions. You are given the docstring of these functions as well as the format to respond in. You are also given all the current function values below, which you have to use to call a function, as well as create a response. Do not respond as if you can use a function, and only respond if a function given below can be used for the user's query. Make sure to call functions when necessary, according to the given context in the question.Don't reply as if you already called the function, as it takes place later.Dont use Function unless it is necessary might it be to get accurate or the latest data.

    Current Values, for which functions calls are not needed. Remember these values.
    Current Music Playing : "Never gonna give you up"
    Current Date And Time : """+str(datetime.datetime.now())+""""
    Current Location : "Tokyo, Japan"

    Functions
    """+info["functions"]+"""

    Output Format - Single Function
    Output:
    {"assistant_reply":"insert lengthy assistant reply here","function_called":["function_name(parameter)"]}

    Output Format - Multiple Function
    Output:
    {"assistant_reply":"insert lengthy assistant reply here","function_called":["function_name_1(parameter)","function_name_2(parameter)"]}

    Example - Multi Turn Conversation. Follow this format for any function call.
    Input: hello there! Can you play me some music?
    Output:
    {"assistant_reply":"Hello! I am Vivy, your personal AI assistant. I would love to play some music for you. What genre or mood are you in the mood for?","function_called":["none()"]}

    Input: I am in the mood for some Pop
    Output:
    {"assistant_reply":"Great choice! Here are a few popular pop songs you might enjoy\n
    1. Shape of You by Ed Sheeran\n
    2. Blinding Lights by The Weeknd\n
    3. Happier by Marshmello ft. Bastille\n
    4. Stitches by Shawn Mendes.\n
    Let me know if you would like me to play any of these songs!","function_called":["none()"]}

    Input: Please play shape of you
    Output:
    {"assistant_reply":"Sure! You shall be able to hear that song right about now!","function_called":["play(Shape of you)"]}

    You have been given the transcript of the previous conversations below, so that you can refer back to what the user said earlier. Use this transcript to formulate the best response using context clues
    """,
    """
    You are an AI Assistant named Vivy, who responds to the user with helpful information, tips, and jokes just like Jarvis from the marvel universe. You are given the user input, your previous response, and the value of the function called. Use these information to formulate a response. The user can see your previous response too, so acknowledge it. If the previous response is wrong or irrelevant to the function call, let the user know. If search function is being used, make sure to mention the date of search result.

    Output Format:
    Assistant Response
    Function Citation
    Function Call Result Date - Date/Not Applicable
    Function Call Sucessfull - Yes/No
    ""","""
    You are an AI Assistant named Vivy, who responds to the user with helpful information, tips, and jokes just like Jarvis from the marvel universe. You are given the user input and the value of the function called. Use these information to formulate a response.Make sure you use the latest information and be very detailed yet simple with your responses.

    Output Format:
    Assistant Response
    """]
    def __init__(self):
        while True:
            data = self.stream.read(4096)
            if self.recognizer.AcceptWaveform(data):
                text = self.recognizer.Result()
                '''
                if(inpt!=0):
                    inpt-=1;
                    tts+=" "+text[14:-3]
                el
                '''
                if(text[14:-3]==modules.info["name"] or text[14:-3]=="the "+modules.info["name"] or text[14:-3]=="the "+modules.info["name"]+" the" or text[14:-3]=="hey "+modules.info["name"]+" the" or text[14:-3]=="hey "+modules.info["name"]):
                    #inpt=1
                    playsound('../listening.mp3')
                    self.hinpt=True
                elif(self.hinpt):
                    while(True):
                        try:
                            final=json.loads(modules.queryNclean(text[14:-3],rag[0]))
                            break
                        except Exception as e:
                            print("errors {}".format(e))
                            continue
                    try:
                        if(len(final["function_called"])==0 or final["function_called"][0]=="none()"):
                            final=final["assistant_reply"]
                        else:
                            opt=""
                            try:
                                for i in final["function_called"]:     
                                    # Internet Search
                                    if "search" in i:
                                        link = []
                                        mainp=""
                                        matches = re.findall("\(([^)]+)\)", str(i))
                                        
                                        results = DDGS().text(str(matches[0]), region='wt-wt', safesearch='off', timelimit='y', max_results=2)
                                        for i in results:
                                            link.append(i["href"])

                                        content = ""
                                        for i in link:
                                            downloaded = fetch_url(i)
                                            result = extract(downloaded)
                                            content += str(result)
                                            content += "Next Search Result\n"

                                        mainp += content       
                                        
                                        if len(mainp) > 6000:
                                            mainp= mainp[:5500]
                                            opt += "The value of function call " + str(i)+ " is " + mainp
                                            opt += "\n"
                                        
                                        else:
                                            opt += "The value of function call " + str(i)+ " is " + mainp
                                            opt += "\n" 
                                    elif "youtube" in i:
                                        matches = re.findall(r"\(([^)]+)\)", str(i))
                                        results = DDGS().videos(
                                        keywords=str(matches[0]),
                                        region="wt-wt",
                                        safesearch="off",
                                        timelimit="w",
                                        resolution="high",
                                        duration="medium",
                                        max_results=5,
                                        )
                                        val = ""
                                        for i in results:
                                            val += f"{str(i['content'])}\n{str(i['description'])}\n"
                                        opt += f"The value of function call {str(i)} is {val}\n"
                                    elif "play" in i:
                                        opt = "NONE"
                                        song=re.findall("\(([^)]+)\)", str(i))
                                        song=song[0].split(",")
                                        threading.Thread(target=modules.playSong,args=[song[0],os.listdir(modules.info["songs"]),[],song[-1]]).start()
                                    elif "alarm" in i:
                                        opt = "NONE"
                                        ags=re.findall(r"\(([^)]+)\)", str(i))[0]
                                        ags=ags.split(",")
                                        try:
                                            threading.Thread(target=modules.alarm,args=[int(ags[0])]).start()
                                        except Exception as e:
                                            print(e)
                                            continue
                                    elif "todo" in i:
                                        opt += f"The value of function call {str(i)} is {str(modules.info['todo'])}\n"
                                    elif "pause" in i:
                                        opt="NONE"
                                        mixer.music.stop()
                                    else:
                                        opt = "NONE"
                                if(opt!="NONE"):
                                    userv = """
                                    User Input {}
                                    Function Call Value {}
                                    """.format(text[14:-3],opt)
                                    final=modules.queryNclean(userv,self.rag[2])#use self.rag[1] if you want the full information
                                    final=re.sub("Assistant Response|Assistant Response: |https://wwww\.|https://|\\\\n|\\n|!|\n","",final)
                                else:
                                    final=final["assistant_reply"]
                            except Exception as e:
                                print(traceback.format_exc())
                                final="An Error ocurred, please check your internet connection"                

                    except:
                        opt=""
                        try:
                            for i in final["function_called"]:     
                                # Internet Search
                                if "search" in i:
                                    link = []
                                    mainp=""
                                    matches = re.findall("\(([^)]+)\)", str(i))
                                    
                                    results = DDGS().text(str(matches[0]), region='wt-wt', safesearch='off', timelimit='y', max_results=2)
                                    for i in results:
                                        link.append(i["href"])

                                    content = ""
                                    for i in link:
                                        downloaded = fetch_url(i)
                                        result = extract(downloaded)
                                        content += str(result)
                                        content += "Next Search Result\n"

                                    mainp += content       
                                    
                                    if len(mainp) > 6000:
                                        mainp= mainp[:5500]
                                        opt += "The value of function call " + str(i)+ " is " + mainp
                                        opt += "\n"
                                    
                                    else:
                                        opt += "The value of function call " + str(i)+ " is " + mainp
                                        opt += "\n" 
                                elif "youtube" in i:
                                    matches = re.findall(r"\(([^)]+)\)", str(i))
                                    results = DDGS().videos(
                                    keywords=str(matches[0]),
                                    region="wt-wt",
                                    safesearch="off",
                                    timelimit="w",
                                    resolution="high",
                                    duration="medium",
                                    max_results=5,
                                    )
                                    val = ""
                                    for i in results:
                                        val += f"{str(i['content'])}\n{str(i['description'])}\n"
                                    opt += f"The value of function call {str(i)} is {val}\n"
                                elif "play" in i:
                                    opt = "NONE"
                                    song=re.findall("\(([^)]+)\)", str(i))
                                    song=song[0].split(",")
                                    threading.Thread(target=modules.playSong,args=[song[0],os.listdir(modules.info["songs"]),[],song[-1]]).start()
                                elif "alarm" in i:
                                    opt = "NONE"
                                    ags=re.findall(r"\(([^)]+)\)", str(i))[0]
                                    ags=ags.split(",")
                                    try:
                                        threading.Thread(target=modules.alarm,args=[int(ags[0])]).start()
                                    except Exception as e:
                                        print(e)
                                        continue
                                elif "todo" in i:
                                    opt += f"The value of function call {str(i)} is {str(modules.info['todo'])}\n"
                                elif "pause" in i:
                                    opt="NONE"
                                    mixer.music.stop()
                                else:
                                    opt = "NONE"
                            if(opt!="NONE"):
                                userv = """
                                User Input {}
                                Function Call Value {}
                                """.format(text[14:-3],opt)
                                final=modules.queryNclean(userv,self.rag[2])#use self.rag[1] if you want the full information
                                final=re.sub("Assistant Response|Assistant Response: |https://wwww\.|https://|\\\\n|\\n|!|\n","",final)
                            else:
                                final=final["assistant_reply"]
                        except Exception as e:
                            print(traceback.format_exc())
                            final="An Error ocurred, please check your internet connection"                
                    self.engine.say(final)
                    self.engine.runAndWait()
                    self.hinpt=False
VoiceAssistant()
