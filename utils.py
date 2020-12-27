import urllib.request
import chess.pgn
import io
import networkx as nx

depth=10
startFEN="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def download_data(username):
    data=""
    with urllib.request.urlopen("https://lichess.org/api/games/user/"+username) as fp:
        data=fp.read().decode('utf-8')
    return data

def process_data(data):
    flag=True
    pgns=[]
    pgn=""
    for line in data.split('\n'):
        if line=="":
            line=" "
        if line[0]=='[' and flag==True:
            pgn+=line+"\n"
        elif line[0]=='[' and flag==False:
            flag=True
            pgns.append(pgn)
            pgn=""
            pgn+=line+"\n"
        else:
            flag=False
            pgn+=line+"\n"
    return pgns

def getGraphsfromPGNs(pgns,username):
    white=nx.DiGraph()
    black=nx.DiGraph()
    for game in pgns:
        first_game = chess.pgn.read_game(io.StringIO(game))
        board = first_game.board()
        result="lose"
        if first_game.headers.get("White").lower()==username.lower():
            G=white
            if first_game.headers.get("Result")=="1-0":
                result="win"
        else:
            G=black
            if first_game.headers.get("Result")=="0-1":
                result="win"
        if first_game.headers.get("Result")=="1/2-1/2":
                result="draw"
        o=board.fen()
        if o!=startFEN:
            break
        if not G.has_node(o):
            G.add_node(o,games=1,win=0,lose=0,draw=0)
            G.nodes[o][result]=1
        else:
            G.nodes[o]["games"]+=1
            G.nodes[o][result]+=1
        count=0
        for move in first_game.mainline_moves():
            if count==depth:
                break
            board.push(move)
            n=board.fen()
            if not G.has_node(n):
                G.add_node(board.fen(),games=1,win=0,lose=0,draw=0)
                G.nodes[n][result]=1
            else:
                G.nodes[n]["games"]+=1
                G.nodes[n][result]+=1
            if not G.has_edge(o,n):
                G.add_edge(o,n,move=move.uci())
            o=n
            count+=1
    

    return white,black

def getGraphsFromUsername(username):
    data=download_data(username)
    pgns=process_data(data)
    return getGraphsfromPGNs(pgns,username)

if __name__=="__main__":
  white,black=getGraphsFromUsername("DodiyaParth")
  for node in white.nodes:
    print(white.nodes[node],white.in_degree(node),node)
  for node in black.nodes:
    print(black.nodes[node],black.in_degree(node),node)