import serial,time,requests,threading,websocket

PORT="/dev/tty.usbserial-3140"
BAUD=9600

def f(x):
    try:return float(x)
    except:return 0

ser=serial.Serial(PORT,BAUD,timeout=1)
time.sleep(2)

def keep_ws():
    while True:
        try:
            ws=websocket.WebSocket()
            ws.connect("ws://127.0.0.1:8000/ws/esp32")
            while True: ws.recv()
        except:
            time.sleep(2)

threading.Thread(target=keep_ws,daemon=True).start()

frame=[]
print("🌱 LIVE SENSOR STREAM\n")

while True:
    try:
        l=ser.readline().decode(errors="ignore").strip()
        if "*start*" in l: frame=[]; continue
        if l.startswith("*") and ":" in l: frame.append(l)
        if len(frame)>=9:
            d={k:f(v) for k,v in [x.replace("*","").split(":") for x in frame]}
            frame=[]
            payload={
                "N":d.get("n",0),"P":d.get("p",0),"K":d.get("k",0),
                "pH":d.get("ph",7),"temperature":d.get("t",25),
                "humidity":d.get("h",50),"rainfall":0,
                "latitude":d.get("la",0),"longitude":d.get("lo",0)
            }
            requests.post("http://127.0.0.1:8000/ingest",json=payload,timeout=2)
            print("📡",payload)
    except: pass