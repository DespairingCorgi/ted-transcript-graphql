import requests
import os
import json

HEADERS = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}

#language code
langs = [ #해당 코드 외에도 언어 다수 존재 - 언어 리스트를 공개하지는 않았기에 일일이 찾아내봄.
    'bs',#Bosanski
    'id',#Bahasa Indonesia
    'en',#English
    'es',#Español
    'fr',#Français
    'gl',#Galego
    'it',#Italiano
    'hu',#Magyar
    'pl',#Polski
    'pt-br',#Português brasileiro
    'pt',#Português de Portugal
    'ro',#Română
    'vi',#Tiếng Việt
    'tr',#Türkçe
    'el',#Ελληνικά
    'sr',#Српски, Srpski
    'he',#עברית
    'ar',#العربية
    'fa',#فارسى
    'kmr',#کورمانجی
    'hi',#हिन्दी
    'ta',#தமிழ்
    'my',#မြန်မာဘာသာ
    'zh-cn',#中文 (简体)
    'zh-tw',#中文 (繁體)
    'ja',#日本語
    'ko',#한국어
]


URL='https://www.ted.com/graphql'

GETRECENT_VIDEO_QUERY='''
    query ($num_vid: Int!){
        playlists(last: $num_vid){
            edges{
                cursor
                node{
                    slug
                }
            }
        }
    }
'''


GETDATA_QUERY=''' 
    query ($videoId: ID!, $language: String!){
        video(id: $videoId, language:$language){
            title
            slug
            description
            publishedAt
            internalLanguageCode
            hasTranslations
            
            publishedSubtitleLanguages{
                edges{
                    node{
                        internalLanguageCode
                    }
                }
            }
            
        }
    
    translation(language: $language, videoId: $videoId){
        paragraphs{
            cues{
                    text
                }
            }  
        }
    }
    
'''

GETVIDEODATA_QUERY = '''
    query ($videoId:ID!){
        video(id: $videoId){
            title
            slug
            description
            publishedAt
            hasTranslations
            publishedSubtitleLanguages{
                edges{
                    node{
                        internalLanguageCode
                    }
                }
            }
        }
    }

'''

GETTRASCRPITION_QUERY='''
    query getTranscript ($videoId: ID!, $language: String!){
        translation(language: $language, videoId: videoId){
            paragraphs{
                cues{
                    text
                }
            }
        }
    }
    
'''

GETRECENTTALKS_QUERY='''

    query getRecentTalks($first: Int!){
        videos(first: $first){
            edges{
                node{
                    slug
                }
            }
        }
    }

'''


def get_data(vid, lang="en"):
    
    query_var = {"videoId" : vid,"language" : lang}
    res = requests.post(URL, json={"query":GETDATA_QUERY, "variables":query_var})
    
    if res.status_code != 200:
        raise Exception(f"you were not able to get proper response by post: {res}, \n please retry {vid}")
    
    if 'errors' in res.json().keys():
        raise Exception(f"{lang} is not available. you were not able to get from post response: {res.json()['errors'][0]['message']}, \n please retry {vid}")
    
    return res.json()


def get_langlist(vid):
    query_var = {"videoId": vid}
    res = requests.post(URL, json={"query":GETVIDEODATA_QUERY, "variables":query_var})
    
    if res.status_code!=200:
        raise Exception(f"no connection on {vid}")
    
    if 'errors' in res.json().keys():
        raise Exception(f"{vid} got error")
    
    json_object = res.json()
    langlist = [e["node"]["internalLanguageCode"] for e in json_object["data"]["video"]["publishedSubtitleLanguages"]["edges"]]
    
    print("=========================================")
    print(f"Available Languages: {len(langlist)}")
    for l in langlist:
        print(l)
    print("=========================================")
    return json_object
    

def parse_url(url):
    splitted_url = url.split('/')
    return splitted_url[-2] if splitted_url[-1] == 'transcript' else splitted_url[-1]

# def get_transcript(vid, lang):
#     query_var = {"videoId": vid, "language":lang}
#     res = requests.post(URL, json={"query": GETTRASCRPITION_QUERY, "variables":query_var})
    
#     if res.status_code!=200:
#         raise Exception(f"no connection: {lang}\n{vid}")
    
#     if res.json()['errors']:
#         raise Exception(f"{vid} got error on {lang}")
    
#     return res.json()


def parse_data(jsonData, lang):
    
    ###############metadata#############
    slug = jsonData['data']['video']['slug']
    published_at = jsonData['data']['video']['publishedAt']
    #curlang = jsonData['data']['video']['internalLanguageCode']
    curmeta = None
    
    ######## meta 생성, 또는 불러오기########
    curdir = os.getcwd()
    targetdir = os.path.join(curdir, 'TED', slug)
    targetMetaDir = os.path.join(targetdir, 'meta.json')
    if (os.path.exists(targetdir)):
        if(os.path.exists(targetMetaDir)):
            with open(targetMetaDir, 'r', encoding='utf-8-sig') as f:
                curmeta = json.loads(f.read())
        else:
            curmeta = {
                "slug" : slug,
                "published": published_at,
                "languages":[]
            }
    else:
        os.makedirs(targetdir)
        curmeta = {
            "slug" : slug,
            "published": published_at,
            "languages":[]
        }
    
    ####################################
    title = jsonData['data']['video']['title']
    # description 정제
    description = jsonData['data']['video']['description'].replace('\n', '')
    
    # if curlang != lang:
    #     raise Exception(f"the language: {lang} is not available")
    
    #changed curlang to lang
    if lang not in curmeta['languages']:
        curmeta['languages'].append(lang)
    else:
        raise Exception("the file already exists")
    
    if jsonData['data']['translation']:
        transcript = [title, description] #default로 타이틀과 Description이 들어감.
        paragraphs = jsonData['data']['translation']['paragraphs']
        for p in paragraphs:
            #print(paragraphs)
            cue = p['cues']
            p_txt = ''
            for i, txt in enumerate(cue):
                #p_text 정제
                #수정 부분
                #print(i, txt['text'])
                if lang == 'zh-tw' or lang=='zh-cn' or lang == 'ja':
                    p_txt+=txt['text'].replace('\n', '')
                else:
                    p_txt+=(txt['text'].replace('\n', ' ')+' ')
            p_txt = p_txt.strip()
            transcript.append(p_txt)

        ###################name rules#####################
        
        #현재는 slug폴더의 언어 형식으로 정함.
        
        ##################################################

        newfile = os.path.join(targetdir, lang+'.txt')
        f = open(newfile,'w', encoding='utf-8-sig')
        f.write('\n'.join(transcript))
        
        with open(targetMetaDir, 'w', encoding='utf-8-sig') as f:
            f.write(json.dumps(curmeta, ensure_ascii=False, indent=4))
        #print(f"언어: {lang}은 존재합니다.")
    else:
        with open(targetMetaDir, 'w', encoding='utf-8-sig') as f:
            f.write(json.dumps(curmeta, ensure_ascii=False, indent=4))
        raise Exception(f'there is no transcription of {lang}')

# slug = "mesmin_destin_how_everyday_interactions_shape_your_future" such things...

def get_all_transcriptions(slug):
    
    try:
        initialdata = get_langlist(slug)
        #print(initialdata)
    except Exception as e:
        print("connection error occurred")
        raise
    
    
    try:
        langList = [e["node"]["internalLanguageCode"] for e in initialdata["data"]["video"]["publishedSubtitleLanguages"]["edges"]]
    except:
        raise Exception("language does not exits")        
    
    for l in langList:
        try:
            jsonData = get_data(slug, l)
            #break #must be commmented
        except Exception as e:
            print(str(e))
            break            
        try:
            parse_data(jsonData,l)
            #break
        except Exception as e:
            print(str(e))
            #break #must be commented
            continue
        
        #break #must be commented
        
#get_all_transcriptions("mia_kami_mana_salt_water")

# jsonData = get_data(URL, "keenan_norris_one_of_the_most_dangerous_men_in_american_history", 'vi')
# parse_data(jsonData, 'vi')
FILENAME='ted_talks_url.txt'
FINISHED='finished.txt'

def save_transcripts(slugs):
    with open(f'./{FINISHED}', 'r') as f:
        finished_slugs = f.read().split('\n')
    
    f = open(f'./{FINISHED}', 'a+')
    
    for i,s in enumerate(slugs):
        if s not in finished_slugs:
            try:
                get_all_transcriptions(s)
            except:
                print(f"error from {s}")
                raise
            finished_slugs.append(s)
            if not f.read() and not i:
                f.write(s)
            else:
                f.write('\n'+s)
    
    print("successfully finished:", slugs)
    
    f.close()


def get_all_transcriptions_from_file():
    with open(f'./{FILENAME}', 'r') as f:
        slugs = [x.split('/')[-1] for x in f.read().split('\n')]
    save_transcripts(slugs)

def get_recent_videos(n):
    '''
        the most recent talks 'n'
    
    '''
    variables = {"first":n}
    res = requests.post(URL, json={"query": GETRECENT_VIDEO_QUERY, "variables": variables})
    edges = json.loads(res)["data"]["videos"]["edges"]
    slugs = [e["node"]["slug"] for e in edges]
    
    return slugs

#get_all_transcriptions_from_file()
# example_url='tony_long_the_outlaws_of_the_ocean_and_how_we_re_reeling_them_in'
# print(get_data(example_url))

def parse_data2(jsonData, lang):
    # Title 정제
    title = jsonData['data']['video']['title']
    # description 정제
    description = jsonData['data']['video']['description'].replace('\n', '')
    
    if jsonData['data']['translation']:
        transcript = [title, description] #default로 타이틀과 Description이 들어감.
        paragraphs = jsonData['data']['translation']['paragraphs']
        print(f"{lang} - lines: {len(paragraphs)+2}")
        print("=========================================")
        for p in paragraphs:
            cue = p['cues']
            p_txt = ''
            for i, txt in enumerate(cue):
                if lang == 'zh-tw' or lang=='zh-cn' or lang == 'ja':
                    p_txt+=txt['text'].replace('\n', '')
                else:
                    p_txt+=(txt['text'].replace('\n', ' ')+' ')
            p_txt = p_txt.strip()
            transcript.append(p_txt)
    if transcript:
        return transcript
    else:
        raise Exception("the transcript is empty.")