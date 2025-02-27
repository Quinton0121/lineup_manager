
####################################################################
'''

Remember to reset config.json to suit current year application info
***** total interview number must set it to the right number********

------------------------------------------------------
 "init_time": 44966.42055,   
  "last_timevalue": 44999.41963,

  are not in used

'''
#####################################################################



import pandas as pd
import webbrowser
import os #use for new instance of chrome
import json
import re  
#import datetime
# import time, pyautogui
# import keyboard

'''
confirm max line up as 6 people

'''

#constant and global variable , this part will run before any functions
with open('config.json') as f:
        config = json.load(f)
     
total_interview = config['total_interview']
npg = config['npg'] 
#last_timevalue never used
last_timevalue  = config['last_timevalue'] 
last_no = config['last_no']
next_group = config['next_group']
file_name = config['file_name']


with open('data.json') as f:
    data =  json.load(f)
    #print("data: ",data)


with open("./data/"+str(file_name)+".json", "w") as outfile:
    f = json.dumps(data)
    outfile.write(f)
   


with open('config_backup.json',"w") as outfile:
    # .dumps() as a string
    json_string = json.dumps(config)
    outfile.write(json_string)


def jump_in_line(no):
    with open('data.json') as f:
        jump_data =  json.load(f)

    #constant and global variable
    with open('config.json') as f:
            jump_config = json.load(f)
    
    
    jump_config['next_group'].append(no)
 
    jump_data['line'].append(no)
    jump_data['jump_no'].append(no)

    # Writing to sample.json
    with open("data.json", "w") as outfile:
        jump_data_string = json.dumps(jump_data)
        outfile.write(jump_data_string)

    with open('config.json',"w") as outfile:
        # .dumps() as a string
        jump_json_string = json.dumps(jump_config)
        outfile.write(jump_json_string)
    print("*********************************************************************")
    print("************ remember to comment out jump_in_line() *****************")
    print("*********************************************************************")


def read_google_sheet():
    #old sheet
    #SHEET_ID = '1rwLguH8lm0qCUPmzozvCMHCnQrKutPN39YKSpREiJDc'
    SHEET_ID = '1l8cnl6P4VVbTy5JcV0OVeRXg2xWHWy_DveYz6aUf7EU'
    SHEET_NAME = 'lite'
    url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
    df = pd.read_csv(url,error_bad_lines=False)
    #df_sort = df.sort_values(by=['Check-in Time'])
    df_sort = df.sort_values(by=['timevalue'],ascending=True)
    #print(df['Check-in Time'].values[:50])
    #print(df.head(50))
    #print(df_sort['Check-in Time'].values[:50])

    #print(df_sort.iloc[npg-1]['Check-in Time'])

    return df_sort

def get_next_group(df):

    _next_group = []
    i = 0

    count_not_interview = 0 
    for index in range( len(df)): 
        # print(df.ioc[index])
        if df.iloc[index]['Checked In'] == True and df.iloc[index]["No"] not in  data['line']:
            count_not_interview = count_not_interview +1
            print('have not interview: ', df.iloc[index]["No"] )
    
    print('total not interview no: ',count_not_interview - npg)
    print('total interviewed (not included the jump in line for this tv group): ', len(data['line'])+npg )
    while len(_next_group) < npg :
        #print(len(_next_group),npg)
        #print("no, checked in",df.iloc[i]["No"],df.iloc[i]["Checked In"])
        
        # if df.iloc[i]["timevalue"] <= last_timevalue and df.iloc[i]["No"] not in  data['line']:
        #     _next_group.append(int(df.iloc[i]["No"]))

        #cancelled the greater than last_timevalue
        if  df.iloc[i]["No"] not in  data['line'] and df.iloc[i]['Checked In'] == True:
            _next_group.append(int(df.iloc[i]["No"]))
            print("_next_group",_next_group)
        
        if i == total_interview-1:
            print("scanned all, no next group or ***** check total interview number in config.json *****")
            exit()

        i += 1

    #next_group_last_timevalue = df.iloc[i-1]["timevalue"]
    print("next group no: ",_next_group,df.iloc[i-1]["No"])
    return (_next_group,float(df.iloc[i-1]["timevalue"]))


def write_json( _next_group, _next_group_last_timevalue):
    #print("data line before: ",data['line'])
    for num in _next_group:
        data['line'].append(num)
    
    data["npg"].append(npg)
    #print("data line after: ",data['line'])
    #print("write to json data: ", type(data))
    # Serializing json
    json_object = json.dumps(data, indent=4)


    #update config.json
    config['next_group'] = _next_group
    config['last_timevalue'] = _next_group_last_timevalue
    config['last_no'] = _next_group[-1]
    config['file_name'] = file_name + 1
    config['number_of_people_interviewed'] = config['number_of_people_interviewed'] + npg


    # Writing to sample.json
    with open("data.json", "w") as outfile:
        outfile.write(json_object)

    with open('config.json',"w") as outfile:
        # .dumps() as a string
        json_string = json.dumps(config)
        outfile.write(json_string)
    #df_sort.to_csv("1.csv", encoding = "GB18030")



def write_html():
    #constant and global variable
    with open('config.json') as f:
            new_config = json.load(f)


    #for the beginning of the card number
    temp_number = ["000","000","000","000","000","000"]

    last_group_index = 0
    if len(data["npg"]) >= 2 :
        last_group_index = data["npg"][-2] + data["npg"][-1] 

        for i in range(data["npg"][-2]):
            temp_number[i] = data['line'][-(last_group_index - i)]

    #number on the back 
    number_on_card1,number_on_card2,number_on_card3,number_on_card4,number_on_card5,number_on_card6 = temp_number


  
    #reset - backcard to 000
    #number_on_card1,number_on_card2,number_on_card3,number_on_card4,number_on_card5,number_on_card6 = [000,000,000,000,000,000]
    
    #card_num 是next_group + " " ，card_num 總數為6
    new_next_group = new_config["next_group"]
    card_num = new_next_group
    group_len = len(new_next_group)

    for i in range( 6 - group_len):
        card_num.append("000")

     #--------------------------------------------writing html--------------------------------------   

    #html_string = ""
    f = open('index.html', 'r',encoding='utf-8')
    # writing the code into the file


    html_string = f.read()

    # close the file
    f.close()
    #print("card_num: ",card_num)
    #html_string = html_string.replace('Qoos2',df_time)
    html_string = re.sub(r'id="Qoos1">[0-9]*</h1>', 'id="Qoos1">'+str(number_on_card1)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos2">[0-9]*</h1>', 'id="Qoos2">'+str(card_num[0])+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos3">[0-9]*</h1>', 'id="Qoos3">'+str(number_on_card2)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos4">[0-9]*</h1>', 'id="Qoos4">'+str(card_num[1])+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos5">[0-9]*</h1>', 'id="Qoos5">'+str(number_on_card3)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos6">[0-9]*</h1>', 'id="Qoos6">'+str(card_num[2])+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos7">[0-9]*</h1>', 'id="Qoos7">'+str(number_on_card4)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos8">[0-9]*</h1>', 'id="Qoos8">'+str(card_num[3])+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos9">[0-9]*</h1>', 'id="Qoos9">'+str(number_on_card5)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos10">[0-9]*</h1>', 'id="Qoos10">'+str(card_num[4])+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos11">[0-9]*</h1>', 'id="Qoos11">'+str(number_on_card6)+'</h1>', html_string)
    html_string = re.sub(r'id="Qoos12">[0-9]*</h1>', 'id="Qoos12">'+str(card_num[5])+'</h1>', html_string)
    html_string = html_string.replace('#ee6b6e;color: black;','QoosColor1')
    html_string = html_string.replace('#2980b9;color: white;','QoosColor2')
    html_string = html_string.replace('QoosColor2','#ee6b6e;color: black;')
    html_string = html_string.replace('QoosColor1','#2980b9;color: white;')

    
    
    with open("index.html", "w",encoding='utf-8') as file:
        file.write(html_string)

# html_template = """<html>
# <head>
# <title>Title</title>
# </head>
# <body>
# <h2>Welcome To GFG</h2>
  
# <p>Default code has been loaded into the Editor.</p>
  
# </body>
# </html>
# """



# # #register the browser
# # chrome_path = "/Applications/Google Chrome.app"
# # webbrowser.register('chrome',webbrowser.BackgroundBrowser(chrome_path),1)




def open_webpage():
    # #open new instance of chrome
    filename = 'file:///'+os.getcwd()+'/' + 'index.html'
    # #browser= webbrowser.get('chrome')
    # #browser= webbrowser.get('Safari')
    webbrowser.open(filename,new = 0, autoraise=True)
    print("opened webpage")


# time.sleep(3)
# #mac
# #pyautogui.hotkey('ctrl','tab')
# # press CTRL button
# keyboard.press("ctrl")
# print("ctrl pressed")

# time.sleep(1)
# keyboard.press("tab")
# print('tab pressed')

# time.sleep(1)
# # release the CTRL button
# keyboard.release("ctrl")
# keyboard.release("tab")
# print("all key released")

# # #windows
# # pyautogui.hotkey('ctrl','tab')
# pyautogui.hotkey('ctrl', 'w')


def reset():

    reset_config = {
        "beautify JSON": "cmd + shift + j",
        "total_interview": 748,
        "npg": 5,
        "init_time": 44966.42055,
        "last_timevalue": 44966.42055,
        "last_no": 0,
        "number_of_checked_in": 0,
        "number_of_not_check_in": 0,
        "next_group": [
        
        ],
        "number_of_people_interviewed": 0,
        "file_name":0
    }

    reset_json_object = {
        "npg": [
        
        ],
        "line": [
        
        ],
        "jump_no":[]
    }

    reset_json_object_string = json.dumps(reset_json_object, indent=4)

    with open("data.json", "w") as outfile:
        outfile.write(reset_json_object_string)

    with open('config.json',"w") as outfile:
        # .dumps() as a string
        rest_json_string = json.dumps(reset_config)
        outfile.write(rest_json_string)

    write_html()
    open_webpage()





def main():

    #-------------------------------------------------------------------------
    df_sort = read_google_sheet()
    _next_group, next_group_last_timevalue= get_next_group(df_sort)
    
    write_json( _next_group, next_group_last_timevalue)

    #-------------------------------------------------------------------------
    #***jump in line has to happen after write json, since next group will rewrite json
    #   and globel data has declared before writing to jump_data, no matter where the 
    #   jump_in_line function call
    
    # jump_in_line(711)

    #-------------------------------------------------------------------------
    write_html()
    open_webpage()

if __name__ == "__main__":
    main()










# reset()


