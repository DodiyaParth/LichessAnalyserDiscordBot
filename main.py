import discord
import os
import requests
import json
from keep_alive import keep_alive
from utils import *
from cairosvg import svg2png
import emoji

token = os.environ.get("TOKEN")
client = discord.Client()
usernames={}
colors={}
nodeFENs={}
Graphs={}
fenStack={}

def stats(G,server):
  result=""
  current=nodeFENs[server]
  result+="overall stats from here,\n"+str(G.nodes[current])
  for child in G.successors(current):
    result+="\nmove : "+str(G[current][child]['move'])
    result+=" "+str(G.nodes[child])
  return result

def checkUsername(uname):
  try:
    response = requests.get('https://lichess.org/api/user/'+uname)
    json_data = json.loads(response.text)
    return True
  except:
    print("Invalid Username")
    return False

def get_quote():
  response = requests.get('https://www.zenquotes.io/api/random')
  json_data = json.loads(response.text)
  quote = json_data[0]['q']
  return quote

def boardImage(fen,color):
  board=chess.Board()
  flipped=False
  if color=="b":
    flipped=True
  board.set_fen(fen)
  svg_img=chess.svg.board(board,flipped=flipped, size=350)
  svg2png(bytestring=svg_img,write_to='output.png')
  return


@client.event
async def on_ready():
  print("Logged in : ", client)


@client.event
async def on_message(msg):

  if msg.author == client.user:
    return
  
  server=msg.channel.guild
  if server not in usernames.keys():
    usernames[server]=""
  if server not in colors.keys():
    colors[server]=""
  if server not in nodeFENs.keys():
    nodeFENs[server]=startFEN
  if server not in fenStack.keys():
    fenStack[server]=[startFEN]
  

  print(msg.author , " : " , msg.content )

  if msg.content.startswith("$insp"):
    quote = get_quote()
    await msg.channel.send(quote)
    return
  
  if msg.content.startswith("$help"):
    await msg.channel.send("I will add this feature later!")
    return
  
  if msg.content.startswith("$username"):
    uname=msg.content[9:].strip()
    if uname=="":
      print("Get Username")
      await msg.channel.send("Username : "+usernames[server])
      return
    else:
      if not checkUsername(uname):
        print(uname+" is not real Lichess username.")
        await msg.channel.send(uname+" is not real Lichess username.")
        return
      usernames[server]=uname
      await msg.channel.send("Please wait, We are processing your data!")
      white,black=getGraphsFromUsername(uname)
      Graphs[server]={}
      Graphs[server]['w']=white
      Graphs[server]['b']=black
      nodeFENs[server]=startFEN
      print("Set Username to "+uname)
    await msg.channel.send("We are ready to serve stats for "+usernames[server])
    return
  

  if msg.content.startswith("$color"):
    color=msg.content[6:].strip()
    if color=="":
      print("Get Color")
      await msg.channel.send("Color : "+colors[server])
    else:
      if color=="w" or color=="b":
        colors[server]=color
        nodeFENs[server]=startFEN
        print("Set Color to "+color)
        await msg.channel.send("Color : "+colors[server])
      else:
        await msg.channel.send("Send valid color code \'w\' or \'b\'")
    return
  
  checkList=['restart','move','current','back','turn','stats']
  for item in checkList:
    if msg.content.startswith('$'+item):
      if usernames[server]=="":
        await msg.channel.send("Set username first")
        return
      elif colors[server]=="":
        await msg.channel.send("Set color first")
        return

  G=Graphs[server][colors[server]]

  if msg.content.startswith("$current"):
    boardImage(nodeFENs[server],colors[server])
    with open('output.png', 'rb') as fp:
      await msg.channel.send(file=discord.File(fp, 'board.png'))

  if msg.content.startswith("$restart"):
    nodeFENs[server]=startFEN
    fenStack[server]=[startFEN]
    await msg.channel.send(emoji.emojize(":thumbs_up:"))
    return


  if msg.content.startswith("$turn"):
    await msg.channel.send("Turn : "+nodeFENs[server].split(' ')[1])
    return
  
  if msg.content.startswith("$move"):
    move=msg.content[5:].strip()
    current=nodeFENs[server]
    stack=fenStack[server]
    validMoves=[]
    for child in G.successors(current):
      edge=G[current][child]['move']
      validMoves.append(edge)
      if edge==move:
        stack.append(child)
        nodeFENs[server]=child
        await msg.channel.send("found move in Database!")
        boardImage(nodeFENs[server],colors[server])
        with open('output.png', 'rb') as fp:
          await msg.channel.send(file=discord.File(fp, 'board.png'))
        await msg.channel.send(stats(G,server))
        return
    #No move matched
    await msg.channel.send("We could not find your move in database!\nvalid moves : "+str(validMoves))

  if msg.content.startswith("$back"):
    current=nodeFENs[server]
    stack=fenStack[server]
    print(current,stack)
    if len(stack)==1:
      await msg.channel.send("You are at the starting position!")
      return
    stack.pop()
    nodeFENs[server]=stack[-1]
    await msg.channel.send(emoji.emojize(":thumbs_up:"))
    return



  if msg.content.startswith("$stats"):
    boardImage(nodeFENs[server],colors[server])
    with open('output.png', 'rb') as fp:
      await msg.channel.send(file=discord.File(fp, 'board.png'))
    #result=stats(G,server)
    # current=nodeFENs[server]
    # result+="overall stats from here,\n"+str(G.nodes[current])
    # for child in G.successors(current):
    #   result+="\nmove : "+str(G[current][child]['move'])
    #   result+=" "+str(G.nodes[child])
    await msg.channel.send(stats(G,server))
    return


keep_alive()
client.run(token)