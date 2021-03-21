import pandas as pd
from utils.exceptions import WrongDataFrameSize, NoScanAvailable
from IPython.core.debugger import Tracer; debughere = Tracer()
import json


def extract_scan(df, ip="", protocol="tcp"):
    if ip:
        scan = df[df["ip"] == ip][protocol].iloc[0]
    else:
        if not isinstance(df,pd.core.series.Series):
            raise WrongDataFrameSize
            return -1
        else:
            scan = df[protocol]
    if scan:
        scan = json.loads(scan)
    else:
        raise NoScanAvailable
        return -1

    scan = [dict(scan[x],**{"port":x}) for x in list(scan.keys()) ]
    scan_df = pd.DataFrame([scan[0]])
    if len(scan) > 1:
        return scan_df.append(scan[1:], ignore_index=True)
    else:
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

