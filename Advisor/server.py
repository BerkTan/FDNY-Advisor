from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib, json, pickle, datetime, pandas as pd

hostName = "localhost"
serverPort = 8000

i = 0

def predict(df, model_dict):
    res = []
    for i,row in df.iterrows():
        itype = int(row.INCIDENT_TYPE_DESC)
        pud = int(row.PROPERTY_USE_DESC)
        if not itype in model_dict.keys() or not pud in model_dict[itype].keys():
            # This combination was not in the training data! return 0
            print("Fail; missing in data")
            res.append(0)
            continue
        df = pd.DataFrame(data=[list(row)], columns=df.columns)
        res.append(model_dict[itype][pud].predict(df[["BOROUGH_DESC","SEASON","TIME_OF_DAY","WEEKDAY"]])[0])
    return res
class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open("base.html","rb") as file:
            base = file.read()
        self.wfile.write(base)
    

    
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        post_data = urllib.parse.parse_qs(self.rfile.read(length).decode('utf-8'))

        self.send_response(201)
        self.end_headers()

        # ##################### #
        # INPUT IS IN POST DATA #
        # ##################### #
        borough = post_data['borough'][0]
        prop_use = post_data['property-use'][0]
        i_type = post_data['incident-type'][0]
        time_of_day = post_data['time'][0]

        # Parse weekday and season from date
        timetup = datetime.datetime.strptime(post_data['date'][0], '%Y-%m-%d').timetuple()
        weekday = timetup.tm_wday
        season = -1
        if timetup.tm_mon < 3 or timetup.tm_mon == 12:
            season = 0
        elif timetup.tm_mon < 6:
            season = 1
        elif timetup.tm_mon < 9:
            season = 2
        else:
            season = 3
        
        print("Received prediction request")
        print("Borough: ",borough)
        print("Incident type: ",i_type)
        print("Property use: ",prop_use)
        print("Time of day: ",time_of_day)
        print("Weekday: ",weekday)
        print("Season: ",season)

        # Do predicting, processing

        # Predict units on scene
        i=0
        uos_mdl_dict = {}
        with open('uos_dict_bayesian.pickle','rb') as file:
            uos_mdl_dict = pickle.load(file)

        df = pd.DataFrame([[i_type,prop_use,borough,season,time_of_day,weekday]]) 
        df.columns = ["INCIDENT_TYPE_DESC","PROPERTY_USE_DESC","BOROUGH_DESC", "SEASON", "TIME_OF_DAY","WEEKDAY"]
        uos = predict(df, uos_mdl_dict)[0]
        print(uos)
        del uos_mdl_dict

        # Predict total incident duration
        i=0
        tid_mdl_dict = {}
        with open('tid_dict_bay.pickle','rb') as file:
           tid_mdl_dict = pickle.load(file)

        df = pd.DataFrame([[i_type,prop_use,borough,season,time_of_day,weekday]]) 
        df.columns = ["INCIDENT_TYPE_DESC","PROPERTY_USE_DESC","BOROUGH_DESC", "SEASON", "TIME_OF_DAY","WEEKDAY"]
        tid = predict(df, tid_mdl_dict)[0]
        print(tid)

        del tid_mdl_dict

        # Predict actions
        #at1_model
        i=0
        at1_mdl_dict = {}
        with open('at1_dict_ridge.pickle','rb') as file:
           at1_mdl_dict = pickle.load(file)

        df = pd.DataFrame([[i_type,prop_use,borough,season,time_of_day,weekday]]) 
        df.columns = ["INCIDENT_TYPE_DESC","PROPERTY_USE_DESC","BOROUGH_DESC", "SEASON", "TIME_OF_DAY","WEEKDAY"]
        at1 = predict(df, at1_mdl_dict)[0]
        print(at1)

        del at1_mdl_dict

        # at2_model
        i=0
        at2_mdl_dict = {}
        with open('at2_dict_ridge.pickle','rb') as file:
           at2_mdl_dict = pickle.load(file)

        df = pd.DataFrame([[i_type,prop_use,borough,season,time_of_day,weekday]]) 
        df.columns = ["INCIDENT_TYPE_DESC","PROPERTY_USE_DESC","BOROUGH_DESC", "SEASON", "TIME_OF_DAY","WEEKDAY"]
        at2 = predict(df, at2_mdl_dict)[0]
        print(at2)

        del at2_mdl_dict

        # at3_model
        i=0
        at3_mdl_dict = {}
        with open('at3_dict_ridge.pickle','rb') as file:
           at3_mdl_dict = pickle.load(file)

        df = pd.DataFrame([[i_type,prop_use,borough,season,time_of_day,weekday]]) 
        df.columns = ["INCIDENT_TYPE_DESC","PROPERTY_USE_DESC","BOROUGH_DESC", "SEASON", "TIME_OF_DAY","WEEKDAY"]
        at3 = predict(df, at3_mdl_dict)[0]
        print(at3)

        del at3_mdl_dict

        # ################ #
        # PUT RESULTS HERE #
        # ################ #
        codes = pd.read_csv("AT_Codes.csv")
        if (uos == 0 and tid == 0 and at1 == 0 and at2 == 0 and at3 == 0):
            results = {"units-onscene":(str("Unprecedented")),"incident-duration":(str("Unprecedented")),"action1":(str("Unprecedented")), "action2":(str("Unprecedented")), "action3":(str("Unprecedented"))}
        else:
            noOther = str("No other recommendations")
            if (at3 == 0):
                if (at2 == 0):
                    results = {"units-onscene":(str(int(uos)) + "  units"),"incident-duration":(str(float(round(tid/60, 2))) + "  minutes"),"action1":str("    " + str(at1) + " - " + list(codes.loc[codes['CODE'] == at1, 'TEXT'])[0] + "\n"), "action2":str(noOther), "action3":str(noOther)}
                else:
                    results = {"units-onscene":(str(int(uos)) + "  units"),"incident-duration":(str(float(round(tid/60, 2))) + "  minutes"),"action1":str("    " + str(at1) + " - " + list(codes.loc[codes['CODE'] == at1, 'TEXT'])[0] + "\n"), "action2":str("    " + str(at2) + " - " + list(codes.loc[codes['CODE'] == at2, 'TEXT'])[0] + "\n"), "action3":str(noOther)}
            else:
                results = {"units-onscene":(str(int(uos)) + "  units"),"incident-duration":(str(float(round(tid/60, 2))) + "  minutes"),"action1":str("    " + str(at1) + " - " + list(codes.loc[codes['CODE'] == at1, 'TEXT'])[0] + "\n"), "action2":str("    " + str(at2) + " - " + list(codes.loc[codes['CODE'] == at2, 'TEXT'])[0] + "\n"), "action3":str("    " + str(at3) + " - " + list(codes.loc[codes['CODE'] == at3, 'TEXT'])[0] + "\n")}
        print(results)

        # Send results
        self.wfile.write(json.dumps(results).encode())

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        webServer.server_close()
        print("Server stopped.")
        quit()