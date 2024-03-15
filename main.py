from graphqlCrawler import *

MYURL = "https://www.ted.com/talks/tombo_banda_meet_mini_grids_the_clean_energy_solution_bringing_power_to_millions" #TED talks URL here
MYLANG = ["en", "id"]#Your language code here

if __name__ == "__main__":
    vid = parse_url(MYURL)
    print(vid)
    get_langlist(vid)
    for lang in MYLANG:
        try:
            data = parse_data2(get_data(vid, lang), lang)
            with open(f"{vid}.{lang}", "w", encoding="utf-8") as f:
                for i,line in enumerate(data):
                    if i < len(data)-1:
                        f.write(line+"\n")
                    else:
                        f.write(line)
        except Exception as e:
            #print(e)
            print(f"The language [{lang}] does not exist")
            print("=========================================")