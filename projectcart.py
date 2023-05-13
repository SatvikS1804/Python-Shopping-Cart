
import pymysql as db
from datetime import datetime
import matplotlib.pyplot as py
import speech_recognition as sr 
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
import re
from word2number import w2n
cnx=db.connect(user='root',password='root',
               host='localhost',
               database='test',
               charset='utf8')
cmd=cnx.cursor()

def common(lst1, lst2): 
    return list(set(lst1) & set(lst2))

def listToString(s):
 
    # initialize an empty string
    str1 = ""
 
    # traverse in the string
    for ele in s:
        str1 += ele
 
    # return string
    return str1

while True:
    print("------------------------------------------------------------------------")
    print("1 - Add products")
    print("2 - User")
    print("3 - Exit")
    print("------------------------------------------------------------------------")
    print("Enter option")
    c=int(input())
    if c == 1:
        while True:
            print("------------------------------------------------------------------------")
            print("1 - Add Product")
            print("2 - Modify cost")
            print("3 - Delete Product")
            print("4 - List All")
            print("5 - Exit")
            print("------------------------------------------------------------------------")
            print("Enter option")
            ch=int(input())
            if ch==1:
                p_id = input("Enter pid -")
                p_name = input("Enter pname -")
                p_category = input("Enter category -")
                p_cost = input("Enter cost -")
                query = "insert into product(pid,pname,category,cost) values({0},'{1}','{2}',{3})".format(p_id, p_name,p_category,p_cost)
                cmd.execute(query)
                cnx.commit()
            elif ch==2:
                p_id=input("Enter the product id -")
                n_cost = input("Enter the updated cost -")
                query ="Update product set cost = {0} Where pid = {1}".format(n_cost,p_id)
                cmd.execute(query)
                cnx.commit()
            elif ch==3:
                print("Enter the pid of the product to be deleted -")
                p_id = input()
                query ="Delete From product Where pid={0}".format(p_id)
                cmd.execute(query)
                cnx.commit()
            elif ch==4:
                query = "Select * From product"
                cmd.execute(query)
                for (c1,c2,c3,c4) in cmd:
                    print("Product ID - {0},Product Name -'{1}',Category -'{2}',Price - Rs {3}".format(c1,c2,c3,c4))
            elif ch==5:
                cmd.close()
                break
    if c==2:
        while True:
            print("------------------------------------------------------------------------")
            print("1 - Buy")
            print("2 - Analysis (Graphical Representation)")
            print("3 - Interactive Mode (Voice based search)")
            print("4 - Exit")
            print("------------------------------------------------------------------------")
            print("Enter option")
            opt=int(input())
            if opt==1:
                query = "Select * From product"
                cmd.execute(query)
                for (c1,c2,c3,c4) in cmd:
                    print("Product ID - {0},Product Name -'{1}',Category -'{2}',Price - Rs {3}".format(c1,c2,c3,c4))
                    
                p_id=input("Enter the product id that you want to buy: ")
                query1="SELECT category FROM product WHERE pid={0}".format(p_id)
                p_category=cmd.execute(query1)
                catavail=-1
                category=" "
                for cat in cmd:
                    catavail=cat[0]
                    category=category+cat[0]
                   
                if catavail==-1:
                    print("Product doesnot exist for that product id")
                else:
                    d = datetime.now()
                    query="INSERT INTO tracker (pid,category,dt) values ({0},'{1}','{2}') ".format(p_id,category,d)
                    cmd.execute(query)
                    print("Thanks for buying")
                cnx.commit()
                
            elif opt==2:
                query="Select category , count(*) from tracker group by category"
                d=cmd.execute(query)
                x=[]
                y=[]
                for (f1,f2) in cmd:
                    x.append(f1)
                    y.append(f2)
                py.bar(x,y,width=0.1)
                py.show()
            elif opt==3:
               r = sr.Recognizer()

               # a function that splits the audio file into chunks
               # and applies speech recognition
               def get_large_audio_transcription(path):
                   """
                   Splitting the large audio file into chunks
                   and apply speech recognition on each of these chunks
                   """
                   # open the audio file using pydub
                   sound = AudioSegment.from_wav(path)  
                   # split audio sound where silence is 700 miliseconds or more and get chunks
                   chunks = split_on_silence(sound,
                       # experiment with this value for your target audio file
                       min_silence_len = 500,
                       # adjust this per requirement
                       silence_thresh = sound.dBFS-14,
                       # keep the silence for 1 second, adjustable as well
                       keep_silence=500,
                   )
                   folder_name = "audio-chunks"
                   # create a directory to store the audio chunks
                   if not os.path.isdir(folder_name):
                       os.mkdir(folder_name)
                   whole_text = ""
                   # process each chunk 
                   for i, audio_chunk in enumerate(chunks, start=1):
                       # export audio chunk and save it in
                       # the `folder_name` directory.
                       chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
                       audio_chunk.export(chunk_filename, format="wav")
                       # recognize the chunk
                       with sr.AudioFile(chunk_filename) as source:
                           audio_listened = r.record(source)
                           # try converting it to text
                           try:
                               text = r.recognize_google(audio_listened)
                           except sr.UnknownValueError as e:
                               print("Error:", str(e))
                           else:
                               text = f"{text.capitalize()}. "
                               print(chunk_filename, ":", text)
                               whole_text += text
                   # return the text for all chunks detected
                   return whole_text

               with sr.Microphone() as source:
                   # read the audio data from the default microphone
                   audio_data = r.record(source, duration=5)
                   print("Recognizing...")
                   # convert speech to text
                   text = r.recognize_google(audio_data)
                       #Query the products
                       
                   t=any(map(str.isdigit, text))
                   if t==True:
                       temp = re.findall('\d+', text)
                       query = "SELECT category , COUNT(category) FROM `tracker` GROUP BY category ORDER BY COUNT(category) DESC LIMIT {0}".format(temp[0])
                       cmd.execute(query)      
                       for f1,f2 in cmd:
                           print("Product :{0}, Number of times product {0} bought: {1} times".format(f1,f2))
                
                   else:
                      tex=text.split(" ")
                      L=['one','two','three','four','five','six','seven','eight','nine','ten']
                      d=common(L,tex)
                      print(d)
                      e=listToString(d)
                      print(e)
                      res = w2n.word_to_num(e)
                      print(res)
                      query = "SELECT category , COUNT(category) FROM `tracker` GROUP BY category ORDER BY COUNT(category) DESC LIMIT {0}".format(res)
                      cmd.execute(query)      
                      for f1,f2 in cmd:
                          print("Product :{0}, Number of times product {0} bought: {1} times".format(f1,f2))
            elif opt==4:
                cmd.close()
                break
            
    if c==3:
          break