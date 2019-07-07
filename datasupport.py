import pandas as pd
from exceptions import WrongDataFrameSize, NoScanAvailable
from IPython.core.debugger import Tracer; debughere = Tracer()
import json


def extract_scan(df ,ip="",protocol='tcp'):
    no_scan = []
    if ip: 
        scan = df[df["ip"] == ip][protocol].iloc[0]
    else:
        if not isinstance(df,pd.core.series.Series):
            raise WrongDataFrameSize
            pass
        else:
            scan = df[protocol]
    
    scan_df = pd.DataFrame(columns=['conf', 'cpe', 'extrainfo', 'name', 'port', 'product', 'reason', 'state', 'version'])
    
    if isinstance(scan,str):
        scan = json.loads(scan)
        scan = [dict(scan[x],**{"port":x}) for x in list(scan.keys()) ]
        scan_df = scan_df.append(scan[0], ignore_index=True)
        
        
        if len(scan) > 1:
            scan_df = scan_df.append(scan[1:], ignore_index=True)
            scan_df.insert(0,"ip",ip, allow_duplicates=True)
            return scan_df
        else:
            scan_df.insert(0,"ip",ip, allow_duplicates=True)
            return scan_df

    
    else:
        
        scan_df = scan_df.append({col: "noscan" for col in scan_df.columns}, ignore_index=True)
        scan_df.insert(0,"ip",ip, allow_duplicates=True)
        return scan_df


def ap_validate_scan(row):
    ### tcp ###
    try:
        scan_df = extract_scan(row)
    except NoScanAvailable:
        row['host'] = 'down'
        return row
    if 1*(scan_df['state'] == "open").sum() > 0:
        row['host'] = "up"
    else:
        row['host'] = "verify"

    #### check for port type ####
    webfilt = scan_df[scan_df['port'].isin(["80","81","8080","8081","443","4443"])]
    if not webfilt.empty:
        row['web'] = ":".join(list(webfilt.port))
    '''
    elif row['port'] in ["22"]:
        row['type'] = "ssh"
    else:
        row['type'] = "verify"
    '''
    return row

