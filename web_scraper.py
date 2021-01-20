import io
import re
import regex
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import pickle

def web_crawler(url1):
    """
    finds and extracts relevant links from a starter page and puts them in a queue.
    :param url1: the url of the starter page
    :return: a list of urls we use later
    """
    url = url1  # the url we begin on
    r = requests.get(url)  # get the webpage into a response object
    data = r.text  # and read the content of the server's response into data
    s = BeautifulSoup(data, "html.parser")  # and create yourself a soup object

    counter = 0  # used to narrow down what websites we're saving
    url_list = []  # saves all the url soup boys
    url_string = []  # used to navigate duplicates

    # we also need a list of urls we don't want to include
    forbidden_url = ["http://volleyball.org/history.html", "http://www.volleyball.com/volleyball_history.aspx",
                     "http://www1.ncaa.org/membership/governance/sports_and_rules_ctees/playing_rules/volleyball/changes_memo",
                     "http://www.usavolleyball.org/", "https://archive.org/details/volleyballfundam0000dear",
                     "https://books.google.com/books?id=Z2EgTLpHfxEC&pg=PA168&lpg=PA168&dq=prisoner+ball+volleyball#q=prisoner%20ball%20volleyball"]

    with open('urls.txt', 'w') as outfile:
        for link in s.findAll('a'):  # for any hyperlink in the soup object

            temp = link.get('href')  # gets the URL from the <a> tag
            temp_str = str(link.get('href'))  # as well as the text representation of that URL

            flag = False  # used to fix a repeat problem we had occur when I ran program

            for links in url_string:
                if links == temp_str:
                    flag = True

            if flag:
                continue

            if temp_str.startswith('http'):

                if 'http' in temp_str[5:]:  # used to remove urls that have multiple http in them for some reason
                    continue

                if temp_str.endswith('htm') or temp_str.endswith('pdf'):
                    continue

                forbid_flag = False
                for x in forbidden_url:
                    if x in temp_str:
                        forbid_flag = True

                if forbid_flag:
                    continue

                if 'volleyball' in temp_str or 'Volleyball' in temp_str:

                        outfile.write(temp + '\n')  # write the file out to the outfile
                        counter += 1  # increment the counter
                        url_list.append(temp)  # add the soup link to a list. It may be better to add the string rep of this
                        url_string.append(temp_str)

            if counter >= 15:  # we want 15 links only, so return when this is true
                outfile.close()
                return url_string


# determines if an element is visible
def visible(element):
    if element.parent.name in ['style', '[endif]','script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True


def scraping(urls):
    """
    Scraps text off of the websites passed in the list
    :param urls: a list of urls given by the web crawler
    :return:
    """

    counter = 1
    text_list = []

    for my_url in urls:  # go to each url and scrap the text off

        print("Scraping URL number", str(counter) + ":", my_url)

        # used to bypass some weird stuff we were running into
        req = Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})

        html = urlopen(req).read()
        s = BeautifulSoup(html, features="html.parser")


        # kill all script and style elements
        # not completely sure if we need this or not
        for script in s(["script", "style"]):
            script.extract()  # rip it out


        data = s.findAll(text=True)
        result = filter(visible, data)
        temp_list = list(result)
        temp_str = ' '.join(temp_list)

        # open the outfile, write to it, and close it
        outfile_name = "URL_File" + str(counter) + ".txt"
        outfile = io.open(outfile_name, 'w', encoding="utf-8")
        outfile.write(temp_str)
        outfile.close()
        text_list.append(temp_str)

        # increment counter
        counter += 1
    return text_list

# step 3
# method to clean up text
# i think there's still some things that need removing /
# cleaning but unsure of how to implement
def clean(text_list):
    counter = 1
    clean_list = []
    sentence_string = ''

    # go through each url's text
    for text in text_list:
        print("Cleaning text number", str(counter))

        # remove new lines and tabs
        new_str = re.sub(r'\s+', ' ', text)
        new_str = regex.sub(r'[^\p{Latin}\p{posix_punct} \d]', '', new_str)

        # split into sentences
        sents = sent_tokenize(new_str)

        # open the outfile, write to it, and close it
        outfile_name = "Clean_File" + str(counter) + ".txt"
        outfile = io.open(outfile_name, 'w', encoding="utf-8")

        counter += 1
        # write each sentence to an outfile
        for sentence in sents:
            outfile.write(sentence + '\n')
            sentence_string = sentence_string + sentence
        outfile.close()
        clean_list.append(sentence_string)
    return clean_list


# step 4
# method to find important terms, returns top ten most important words
def important_terms(clean_list):
    # string to hold all pages combined
    all_text = ''
    # for each url's cleaned text
    for text in clean_list:
        all_text = all_text + text

    # remove punctuation and lowercase everything
    lower = all_text.lower()
    alpha = re.sub('[^a-z]+', ' ', lower)

    # tokenize
    tokens = word_tokenize(alpha)
    unique_tokens = set(tokens)

    # remove stop words
    stop_words = stopwords.words('english')
    # added some weird words I was encountering to the stoplist
    stop_words += ['u', 'jpg', 'kb', 'mb', 'de']
    important_words = [w for w in tokens if not w in stop_words]
    unique_important = [w for w in unique_tokens if not w in stop_words]

    # create dict for tokens and their count
    word_dict = {unique_important[i] : important_words.count(unique_important[i]) for i in range(0, len(unique_important))}

    # print out top 30 important terms
    sorted_dict = {}
    sorted_dict = sorted(word_dict.items(), key = lambda x: x[1], reverse=True)
    print("Top 30 important terms: ")
    common_words = []
    for i in range(29):
        temp = sorted_dict[i]
        common_words.append(temp)
    for i in range(29):
        print(common_words[i])


# step 5
# I believe the top 10 important terms are:
# volleyball, game, team, ball, league, games, beach, sport, rules, court


# step 6
# takes the top ten terms and stores any sentence that contains that word
def knowledge_base(top_ten):
    # goes through all files and saves any sentence that contains the words!

    master_text = ""  # going to hold all sentences from the files

    # open all cleaned files and sentence tokenize them
    for i in range(1, 15, 1):
        # open the file
        filename = "Clean_file" + str(i) + ".txt"
        open_file = io.open(filename, 'r', encoding="utf-8")
        data = open_file.read()
        master_text = master_text + data

    # after reading in from all files, sentence tokenize everything
    sentences = sent_tokenize(master_text)

    important_words = {}

    # now we go through each important word and save any sentence that contains the word
    for word in top_ten:

        print("Compiling knowledge base for important word:", word)

        sent_list = []

        # go through all the sentences
        for sentence in sentences:

            if len(sentence) > 100:
                continue

            if word in sentence:
                sent_list.append(sentence)

        # and then add the word and sentences into the dict
        important_words[word] = sent_list

    # and finally return the completed dict
    return important_words


if __name__ == "__main__":

    # begin by retrieving 15 urls relevant to starter URL
    relevant_urls = web_crawler('https://en.wikipedia.org/wiki/Volleyball')

    # next, we're going to make a text file for each of the relevant URLs by scraping them
    text_list = scraping(relevant_urls)

    # next, clean each text with the clean method
    clean_list = clean(text_list)

    print("We are generating the important terms now ...")
    important_terms(clean_list)

    # manually determined
    top_ten = ["volleyball", "game", "team", "ball", "league", "games", "beach", "sport", "rules", "court"]

    # filter through words and create dicts of important words and sentences that contain them
    knowledge_dict = knowledge_base(top_ten)

    # will print dict if you would like to see it
    # print(knowledge_dict)

    # create a pickle of the knowledge base
    pickle.dump(knowledge_dict, open("volleyball_knowledgebase.pickle", 'wb'))
