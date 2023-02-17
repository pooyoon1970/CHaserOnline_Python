import time
import requests
import re
import sys
import random
import os
import copy
os.environ["http_proxy"] = "http://proxy.spec.ed.jp:80"
url='http://www7019ug.sakura.ne.jp/CHaserOnline003/user/'
#-------------------------------------------------------------------関数群
#改行、タブ、空白削除処理
def func_replace():
  global code
  code=re.sub("\r","\n",r.text)
  for i in range(10) :
    code=re.sub(" \n","\n",code)
    code=re.sub("\n\n","\n",code)
    code=re.sub("\t"," ",code)
    code=re.sub("　"," ",code)
    code=re.sub("  "," ",code)
#-------------------------------------------------------------------
#サーバ接続処理
def session():
  global s,r,url
  print('接続処理  >>  ',end="")
  s=requests.session()
  r=s.get(url)
  func_replace()
  print('Web Connect!')
#-------------------------------------------------------------------
#ログインチェック
def login_check():
  global s,r,url,play_info
  print('ログイン処理  >>  ',end="")
  r=s.get(url+'UserCheck?user='+play_info['-u']+'&pass='+play_info['-p'])
  func_replace()
  while code.find('user=')>-1 or code.find('pass=')>-1:
    r=s.get(url+'UserCheck?user='+play_info['-u']+'&pass='+play_info['-p'])
    func_replace()
  print('User:'+play_info['-u']+' Login!')
#-------------------------------------------------------------------
#ルーム番号チェック
def roomNumberchek():
  global s,r,url,play_info,code,cnt
  cnt=0
  while code.find('roomNumber=')>-1 and code.find('command1=')<0 :
    print("ルーム選択 "+str(cnt)+"回目  >>  ",end="")
    r=s.get(url+'RoomNumberCheck?roomNumber='+play_info['-r'])
    func_replace()
    cnt=cnt+1
  while code.find('command1=')<0 :
    a=0
  print(play_info['-r'] + ' :: Room in!')
#-------------------------------------------------------------------
#GetReady送信
def GetreadySend():
  global s,r,url,gr_code,code
  while code.find('command1=')>-1 :
    print('GetReady  >>  '+gr_code+"  ",end="")
    r=s.get(url+'GetReadyCheck?command1='+gr_code)
    func_replace()
#-------------------------------------------------------------------
#ReturnCode抽出
def ReturnCodeExtraction():
  global code,code_end,turn,RCode_info,mynum
  if code.find('ReturnCode=')>-1 :
    code1=code[code.find('ReturnCode=')+11:len(code)]
    code_end=code1[0:code1.find('\n')]
    RCode_info=code_end.split(',')
    #第１ターンのReturnCodeより自分の番号を設定する。
    if turn==0 :
      for i in RCode_info :
        if int(i)>=1000 :
          point[str(i)]=-9999
          mynum=i
    print("    ReturnCode="+code_end)
#-------------------------------------------------------------------
#action生成
def ActionGeneration():
  global s,r,url,play_info,code,code_end,cnt,action_code,RCode_info,mynum,action_log,RCode_info_old,gr_code,position,c_pos
  print("ActionMove------------------------------")
  max_Num=0
  pos=0
  cnt=0
  mv_pos=[]
  dict={'u':-3,'r':1,'l':-1,'d':3}
  c_pos_old=c_pos
  #現在ポジション確認開始20200323----------------------------------
  if mynum in RCode_info :
    c_pos=RCode_info.index(mynum)
    print("1000:"+str(c_pos))
  else:
    #現在ポジション計算開始20200219----------------------------------
    dict_pt=0
    if(len(gr_code)==3):
      dict_pt=dict[gr_code[2:]]
      print(str(c_pos)+"="+str(c_pos)+"+"+str(dict_pt))
      c_pos=c_pos+dict_pt
    #現在ポジション計算終了20200219----------------------------------
  #現在ポジション確認終了20200323----------------------------------
  print("len(RCode_info))"+str(len(RCode_info)))
  if len(RCode_info)==4 :
    if c_pos==0 :
      act_p2w=['','pl2wr','pu2wd','plu2wrd'] #Put2walk
      act_w0p=['','pl0wr','pu0wd','plu0wrd'] #Put0walk walk優先
      c_pos=0
      mv_pos=[1,2,3]
    elif c_pos==1 :
      act_p2w=['pr2wl','','pru2wld','pu2wd'] #Put2walk
      act_w0p=['pr0wl','','pru0wld','pu0wd'] #Put0walk walk優先
      c_pos=2
      mv_pos=[0,2,3]
    elif c_pos==2:
      act_p2w=['ps2wu','pld2wru','','pl2wr'] #Put2walk
      act_w0p=['pd0wu','pld0wru','','pl0wr'] #Put0walk walk優先
      c_pos=6
      mv_pos=[0,1,3]
    elif c_pos==3:
      act_p2w=['prd2wlu','ps2wu','pr2wl',''] #Put2walk
      act_w0p=['prd0wlu','pd0wu','pr0wl',''] #Put0walk walk優先
      c_pos=8
      mv_pos=[0,1,2]
  elif len(RCode_info)==6:
    if c_pos == 1 :
      act_p2w=['pr2wl','','pr2wl','pru2wld','pu2wd','plu2wrd'] #Put2walk
      act_w0p=['pr0wl','','pl0wr','pru0wld','pu0wd','plu0wrd'] #Put0walk walk優先
      c_pos=1
      mv_pos=[0,2,3,4,5]
    elif c_pos == 2 :
      act_p2w=['pd2wu','pld2wru','','pl2wr','pu2wd','plu2wrd'] #Put2walk
      act_w0p=['pd0wu','pld0wru','','pl0wr','pu0wd','plu0wrd'] #Put0walk walk優先
      c_pos=3
      mv_pos=[0,1,2,4,5]
    elif c_pos == 3 :
      act_p2w=['prd2wlu','pd2wu','pr2wl','','pru2wld','pu2wd'] #Put2walk
      act_w0p=['prd0wlu','pd0wu','pr0wl','','pru0wld','pu0wd'] #Put0walk walk優先
      c_pos=5
      mv_pos=[0,1,2,3,5]
    elif c_pos == 4 :
      act_p2w=['prd2wlu','pd2wu','pld2wru','pr2wl','','pl2wr'] #Put2walk
      act_w0p=['prd0wlu','pd0wu','pld0wru','pr0wl','','pl0wr'] #Put0walk walk優先
      c_pos=7
      mv_pos=[0,1,2,3,5]
  elif len(RCode_info)==9 :
    act_p2w=['prd2wlu','pd2wu','pld2wru','pr2wl','','pl2wr','pru2wld','pu2wd','plu2wrd'] #Put2walk
    act_w0p=['prd0wlu','pd0wu','pld0wru','pr0wl','','pl0wr','pru0wld','pu0wd','plu0wrd'] #Put0walk walk優先
    c_pos=4
    mv_pos=[0,1,2,3,5,6,7,8]
  #最高点の升目を探す開始　20200123追加終了+++++++++++++++++++++++++++++++++
  random.seed()
  maxp=point[RCode_info[mv_pos[0]]]
  for i in mv_pos : #最高得点のマス目を探す
    if maxp < point[RCode_info[i]] :
      maxp=point[RCode_info[i]]
  #最高点の複数マスからランダムに次を選択する。20200123追加開始+++
  max_Num=[]
  for i in mv_pos :
    if maxp == point[RCode_info[i]] :
      max_Num.append(i) #最高得点を持つ升目をリストに加える
  pos=random.choice(max_Num) #要素をランダムに取り出す
  #最高点の升目を探す終了　20200123追加終了+++++++++++++++++++++++++++++++++
  if int(RCode_info[pos])%1000 == 0 and int(RCode_info[pos])>0 :
    action_code=act_p2w[pos] #敵キャラにｐｕtして逃げる
  else :
    action_code=act_w0p[pos] #得点取得のために移動
  print("action  >>  ",action_code,end="")
#-------------------------------------------------------------------
#action送信
def ActionSend():
  global s,r,url,play_info,code,code_end,cnt,action_code,action_log
  action_log.insert(0,action_code)
  while code.find('command2=')>-1:
    r=s.get(url+'CommandCheck?command2='+action_code)
    func_replace()
#-------------------------------------------------------------------
##送信
def RerunEnd():
  global s,r,url,play_info,code,code_end,cnt,action_code
  print('send  >>  ',end="")
  while code.find('command3=')>-1 :
    r=s.get(url+'EndCommandCheck?command3=%23')
    func_replace()
  print("#")
#-------------------------------------------------------------------
##GetreadyMove
def GerReadyMove():
  global action_code,RCode_info,gr_code,point,RCode_info_old
  global c_pos,c_pos_old
  print("GetReadyMove------------------------------")
  #現在ポジション計算開始20200219----------------------------------
  dict={'u':-3,'r':1,'l':-1,'d':3}
  dict_pt=0
  if(len(action_code)==5):
    dict_pt=dict[action_code[4:]]
  elif (len(action_code)==7):
    dict_pt=dict[action_code[5:6]]+dict[action_code[6:]]
  c_pos_old=c_pos
  c_pos=c_pos_old+dict_pt
  print(str(c_pos)+"="+str(c_pos_old)+"+"+str(dict_pt))
  #現在ポジション計算終了20200219----------------------------------
  gr_code='gr'
  if len(RCode_info)==4 :
    if c_pos==0:
      act_grm=['gr','grr','grd',''] #GetReadyMove
      mv_pos=[0,1,2]
    elif c_pos==2:
      act_grm=['grl','gr','','grd'] #GetReadyMove
      mv_pos=[0,1,3]
    elif c_pos==6:
      act_grm=['gru','','gr','grr'] #GetReadyMove
      mv_pos=[0,2,3]
    elif c_pos==8:
      act_grm=['','gru','grl','gr'] #GetReadyMove
      mv_pos=[1,2,3]
  elif len(RCode_info)==6 :
    if c_pos % 2 == 0 :
      if c_pos == 0 :
        if RCode_info_old[c_pos]==RCode_info[1] and RCode_info_old[c_pos+1]==RCode_info[2] :
          c_pos=1 #4 -(wlu)-> 0 -> 1
        elif RCode_info_old[c_pos]==RCode_info[2] and RCode_info_old[c_pos+1]==RCode_info[3] :
          c_pos=3 #4 -(wlu)-> 0 -> 3
      elif c_pos == 2 :
        if RCode_info_old[c_pos]==RCode_info[3] and RCode_info_old[c_pos-1]==RCode_info[2] :
          c_pos=5 #4 -(wru)-> 2 -> 5
        elif RCode_info_old[c_pos]==RCode_info[1] and RCode_info_old[c_pos-1]==RCode_info[0] :
          c_pos=1 #4 -(wru)-> 2 -> 1
      elif c_pos == 6:
        if RCode_info_old[c_pos]==RCode_info[2] and RCode_info_old[c_pos+1]==RCode_info[3] :
          c_pos=5 #4 -(wld)-> 6 -> 5
        elif RCode_info_old[c_pos]==RCode_info[4] and RCode_info_old[c_pos+1]==RCode_info[5] :
          c_pos=7 #4 -(wld)-> 6 -> 7
      elif c_pos == 8:
        if RCode_info_old[c_pos]==RCode_info[4] and RCode_info_old[c_pos-1]==RCode_info[3] :
          c_pos=7 #4 -(wrd)-> 8 -> 7
        elif RCode_info_old[c_pos]==RCode_info[3] and RCode_info_old[c_pos-1]==RCode_info[2] :
          c_pos=5 #4 -(wrd)-> 8 -> 5
      if len(RCode_info) == len(RCode_info_old) :
          c_pos=c_pos_old
    if c_pos==1:
      act_grm=['grl','gr','grr','','grd',''] #GetReadyMove
      mv_pos=[0,1,2,4]
    elif c_pos==3:
      act_grm=['gru','','gr','grr','grd',''] #GetReadyMove
      mv_pos=[0,2,3,4]
    elif c_pos==5:
      act_grm=['','gru','grl','gr','','grd'] #GetReadyMove
      mv_pos=[1,2,3,5]
    elif c_pos==7:
      act_grm=['','gru','','grl','gr','grr'] #GetReadyMove
      mv_pos=[1,3,4,5]
    else :
      act_grm=['gr']
      mv_pos=[0]
  elif len(RCode_info)==9 :
    c_pos=4
    act_grm=['','gru','','grl','gr','grr','','grd',''] #GetReadyMove
    mv_pos=[1,3,4,5,7]
  #最高点の升目を探す開始　20200219追加終了+++++++++++++++++++++++++++++++++
  random.seed()
  maxp=point[RCode_info[mv_pos[0]]]
  for i in mv_pos : #最高得点のマス目を探す
    if maxp < point[RCode_info[i]] :
      maxp=point[RCode_info[i]]
  #最高点の複数マスからランダムに次を選択する。20200123追加開始+++
  max_Num=[]
  for i in mv_pos :
    if maxp == point[RCode_info[i]] :
      max_Num.append(i) #最高得点を持つ升目をリストに加える
  pos=random.choice(max_Num) #要素をランダムに取り出す
  gr_code=act_grm[pos]
  #最高点の升目を探す終了　20200219追加終了+++++++++++++++++++++++++++++++++
  if pos==-1:
    gr_code="gr"
  print("getreadycode="+gr_code)
##-------------------------------------------------------------------関数群
#-------------------------------------------------------------------メインルーチン
st=0
ed=0
cnt=1
direction="urdl"
code=""
turn=0
action_code=""
gr_code="gr"
acno=0
flg=0
mynum=""
RCode_info=[]
RCode_info_old=[]
action_log=[]
#room=[2850,2851]
room=[2531,2539,2547,2555,2563,2571,2579,2587,2595,2603,2691,2699,
      2722,2723,2724,2725,2726,2728,2729,2742,2743,2744,2745,2746,
      2747,2748,2749,2774,2775,2776,2777,2778,2779,2780,2781,2792,
      2793,2794,2795,2796,2797,2800,2801,2802,2803,2804,2805,2808,
      2809,2810,2811,2812,2813,2816,2817,2818,2819,2820,2821,2824,
      2825,2826,2827,2828,2829,2832,2833,2834,2835,2836,2837,2838,
      2839,2840,2841,2842,2843,2844,2845,2846,2847,2848,2849,2850,
      2851,2852,2853,2854,2855,2856,2857,2858,2859,2860,2861,2862,
      2863,2864,2865,2866,2867,2880,2881,2882,2883,2884,2885,2886,
      2887,2888,2889,2890,2891,2892,2893,2894,2895,2896,2897,2898,
      2899,2900,2901,2902,2903,2904,2905,2906,2907,2908,2909,2910,
      2911,2912,2913,2914,2915,2916,2917,2918,2919,2920,2921,2922,
      2923,2924,2925,2926,2927,2928,2929,2930,2931,2932,2933,2934,
      2935,2936,2937,2938,2939,2940,2941,2942,2943,2944,2945,2946,
      2947,2948,2949,2950,2951,2952,2953,2954,2955,2956,2957,2958,
      2959,2960,2961,2962,2963,2964,2965,2966,2967,2968,2969,2970,
      2971,2972,2973,2974,2975,2976,2977,2978,2979,2980,2981,2982,
      2983,2984,2985,2986,2987,2988,2989,2990,2991,2992,2993,2994,
      2995,2996,2997,2998,2999,3000,3001,3002,3003,3004,3005,3006,
      3007,3008,3009,3010,3011,3012,3013,3014,3015,3016,3017,3018,
      3019,3020,3021,3022,3023,3024,3025,3026,3027,3028,3029,3030,
      3031,3032,3033,3034,3035,3036,3037,3038,3039,3041,3042,3043,
      3044,3045,3046,3047,3048,3049,3050,3051,3052,3053,3054,3055,
      3056,3057,3058,3059,3060,3061,3062,3063,3064,3065,3066,3067,
      3068,3069,3070,3071,3072,3073,3074,3075,3076,3077,3078,3079,
      3080,3081,3082,3083,3084,3085,3086,3087,3088,3089,3090,3091,
      3092,3093,3094,3095,3096,3097,3098,3099,3100,3101,3102,3103,
      3104,3105,3106,3107,3108,3109,3110,3111,3112,3113,3114,3115,
      3116,3117,3118,3119,3120,3121,3122,3123,3124,3125,3126,3127,
      3128,3129,3130,3131,3132,3133,3134,3135]
#room=[2856,2857,2858,2859,2860,2861,2862,2863,2864,2865,2866,2867,
#      2944,2945,2946,2947,2948,2949,2950,2951,2952,2953,2954,2955,
#      2956,2957,2958,2959,2960,2961,2962,2963,2964,2965,2966,2967,
#      2968,2969,2970,2971,2972,2973,2974,2975]
room=[]
#room=[2710,2711,2712,2713,2714,2715,2716,2717,2718,2719,2720,2721,2722,2723,2724,2725,2726,2727,2728,2729,
#        2710,2711,2712,2713,2714,2715,2716,2717,2718,2719,2720,2721,2722,2723,2724,2725,2726,2727,2728,2729,
#        2710,2711,2712,2713,2714,2715,2716,2717,2718,2719,2720,2721,2722,2723,2724,2725,2726,2727,2728,2729,
#        2710,2711,2712,2713,2714,2715,2716,2717,2718,2719,2720,2721,2722,2723,2724,2725,2726,2727,2728,2729,
#         2710,2711,2712,2713,2714,2715,2716,2717,2718,2719,2720,2721,2722,2723,2724,2725,2726,2727,2728,2729,
#         2710,2711,2712,2713,2714,2715,2716,2717,2718,2719,2720,2721,2722,2723,2724,2725,2726,2727,2728,2729,
#         2710,2711,2712,2713,2714,2715,2716,2717,2718,2719,2720,2721,2722,2723,2724,2725,2726,2727,2728,2729]
ranking=[3652,3996]
play_info={'-u':'34162020yurikawa' , '-p':'ivMVn9Zt' , '-r':'ranking'}
#play_info={'-u':'cool21' , '-p':'cool' , '-r':'2530'}
map=[[""]*41]*41                                            #マッピング用２次元配列
player_pos={'x':20 , 'y':20}                                #player相対座標
point={
       '':-300,'0':-29,
       '1':50,'2':-20,'3':10,'5':150,'6':150,'7':150,'8':150,'9':50,
       '12':-300,
       '20':5,'21':5,'22':5,'23':5,
       '30':0,'31':0,'32':0,'33':0,
       '40':5,'41':5,'42':0,'43':0,
       '50':5,'51':5,'52':0,'53':0,
       '60':5,'61':5,'62':5,'63':5,
       '1000':999,'2000':999,'3000':999,'4000':999,'5000':999,'6000':999,'7000':999,'8000':999
       }
position=['lu','u','ru','l','c','r','dl','d','dr'] #charactor position
c_pos=4
act_grm=['','gru','','grl','gr','grr','','grd',''] #GetReadyMove
act_wak=['','wu','','wl','','wr','','wd',''] #Walk
act_p3s=['','pu3su','','pl3sl','','pr3sr','','pd3sd',''] #Put3Search
act_p3l=['','pu3lu','','pl3ll','','pr3lr','','pd3ld',''] #Put3Look
act_p2w=['plu2wrd','pu2wd','pru2wld','pl2wr','','pr2wl','pld2wru','pd2wu','prd2wlu'] #Put2walk put優先
act_w2p=['prd2wlu','ps2wu','pld2wru','pr2wl','','pl2wr','pru2wld','pu2wd','plu2wrd'] #Put2walk walk優先
act_kei=['keilu','','keiru','','','','keild','','keird'] #kei
act_pt0=['','pu0','','pl0','','pr0','','pd0',''] #put0
act_p0w=['plu0wrd','pu0wd','pru0wld','pl0wr','','pr0wl','pld0wru','pd0wu','prd0wlu'] #Put0walk put優先
act_w0p=['prd0wlu','pd0wu','pld0wru','pr0wl','','pl0wr','pru0wld','pu0wd','plu0wrd'] #Put0walk walk優先
act_dig=['dlu','du','dru','dl','','dr','dld','dd','drd'] #dig
#-------------------------------------------------------------------
#メインルーチン
#引数取得
args=sys.argv
mapNumData=[]
for i in range(1,len(args),2):
  play_info[args[i]]=args[i+1]
print(play_info)
if play_info['-r']=='room':
  mapNumData=copy.copy(room)
elif play_info['-r']=='ranking':
  for i in range(ranking[0],ranking[1]+1,1):
    mapNumData.append(i)
else:
  mapNumData.append(play_info['-r'])
for i in mapNumData:
  if i == '0000':
    sys.exit()
  play_info['-r']=str(i)
  for j in range(20):
    print('-',end="")
  print('-')
  try :
    #-------------------------------------------------------------------
    session()
    login_check()
    roomNumberchek()
    #-------------------------------------------------------------------
    #ゲームルーチン
    while code.find('user=')==-1 and code.find('command1=')>-1:
      #GetReady送信
      GetreadySend()
      #ReturnCode抽出
      ReturnCodeExtraction()
      #action生成
      ActionGeneration()
      RCode_info_old=RCode_info
      #action送信
      ActionSend()
      #ReturnCode抽出
      ReturnCodeExtraction()
      #GetReadyMove
      GerReadyMove()
      #RCode_info_old=RCode_info
      ##送信
      RerunEnd()
      turn=turn+1
    #-------------------------------------------------------------------
  except :
    print("処理エラー")
    time.sleep(300)
