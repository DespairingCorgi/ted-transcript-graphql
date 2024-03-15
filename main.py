from graphqlCrawler import *

#트랜스크립트를 다운로드 받고싶은 ted talks 링크
MYURL = "https://www.ted.com/talks/tombo_banda_meet_mini_grids_the_clean_energy_solution_bringing_power_to_millions" #TED talks URL here
#특정 언어의 트랜스크립트만 받는 경우 작성 필수(graphqlCrawler.py의 9번 라인 참조 - 추가언어 존재 가능함.)
MYLANG = ["en", "id"]#Your language code here

if __name__ == "__main__":
    vid = parse_url(MYURL)
    print(vid)
    json_object, lang_lst = get_langlist(vid)
    
    # MYLANG에서 명시한 언어만 다운로드 받는 코드
    
    # for lang in MYLANG:
    #     try:
    #         data = parse_data2(get_data(vid, lang), lang)
    #         with open(f"{vid}.{lang}", "w", encoding="utf-8") as f:
    #             for i,line in enumerate(data):
    #                 if i < len(data)-1:
    #                     f.write(line+"\n")
    #                 else:
    #                     f.write(line)
    #     except Exception as e:
    #         #print(e)
    #         print(f"The language [{lang}] does not exist")
    #         print("=========================================")

    # 해당 링크의 현재 등록된 모든 언어의 트랜스크립트를 다운로드 받는 코드

    # for lang in lang_lst:
    #     try:
    #         data = parse_data2(get_data(vid, lang), lang)
    #         with open(f"{vid}.{lang}", "w", encoding="utf-8") as f:
    #             for i,line in enumerate(data):
    #                 if i < len(data)-1:
    #                     f.write(line+"\n")
    #                 else:
    #                     f.write(line)
    #     except Exception as e:
    #         #print(e)
    #         print(f"The language [{lang}] does not exist")
    #         print("=========================================")
    