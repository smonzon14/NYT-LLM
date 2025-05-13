import time
import pyttsx3
import threading 
from threading import Timer
from queue import Queue
from nltk import tokenize
from feed import Feed
from index import Index
import argparse

rss_feed_urls = ["https://rss.nytimes.com/services/xml/rss/nyt/World.xml", 
               "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", 
               "https://rss.nytimes.com/services/xml/rss/nyt/PersonalTech.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/Jobs.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/RealEstate.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/MostViewed.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/MostShared.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/MostEmailed.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/Education.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/US.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/EnergyEnvironment.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/SmallBusiness.xml",
               "https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml",
            ]

def timeout_handler():
   print("Thread timeout")
   raise Exception("Timeout")

def speak(tn, q, re):
   # print(tn, "started")
   
   engine = pyttsx3.init(driverName='sapi5')
   engine.setProperty('rate', 200)
   voices = engine.getProperty('voices') 
   engine.setProperty('voice', voices[1].id)
   engine.startLoop(useDriverLoop=False)
   
   t = Timer(5, timeout_handler)
   cmd = ""
   while re.is_set():
      cmd = q.get()
      if cmd is None:
         t.start()
         time.sleep(0.01)
      elif cmd == -1:
         break
      else:
         if t.is_alive():
            t.cancel()
         engine.say(cmd)
         engine.iterate()
   engine.endLoop()
   

def read(tn, q, re):
   # print(tn, "started")
   response_txt = ""
   sentence = 1
   for text in response.response_gen:
      print(text, end="", flush=True)
      response_txt += text
      # engine.runAndWait() 
      sentences = tokenize.sent_tokenize(response_txt)
      if len(sentences) > sentence:
         cmd = sentences[sentence-1]
         q.put(cmd)
         sentence = len(sentences)
      if not re.is_set():
         break
   q.put(sentences[-1])
   q.put(-1)
   
def refresh_documents():
   documents = Feed(rss_feed_urls).get_documents()
   return documents

def query_index(query, refresh=False):
   documents = refresh_documents() if refresh else []
   index = Index(documents, load_from_disk=False)
   response = index.query(query)
   return response

def answer_query(query, refresh_documents=False):
   global response
   response = query_index(query, refresh=refresh_documents)
   run_event = threading.Event()
   run_event.set()
   queue = Queue()
   rt = threading.Thread(target=read, args=("Read Thread", queue, run_event))
   st = threading.Thread(target=speak, args=("Speak Thread", queue, run_event))
   rt.start()
   st.start()
   try:
      while st.is_alive() or rt.is_alive():
         time.sleep(0.1)
   except KeyboardInterrupt:
      print("\nUser interrupted the process\n")
      run_event.clear()
      rt.join()
      st.join()


if __name__ == "__main__":
   parser = argparse.ArgumentParser(description="Query the RSS feed index.")
   parser.add_argument("--prompt", type=str, help="The query prompt to answer.")
   parser.add_argument("--refresh", type=bool, help="Refresh the documents before querying.")
   args = parser.parse_args()

   prompt = args.prompt
   refresh = args.refresh if args.refresh is not None else False
   answer_query(prompt, refresh_documents=refresh)
   print("\nDone") 

# response.print_response_stream()
