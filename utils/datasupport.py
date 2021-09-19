import pandas as pd
from utils.exceptions import WrongDataFrameSize, NoScanAvailable
from IPython.core.debugger import Tracer; debughere = Tracer()
import json


def pop_all(l):
    r, l[:] = l[:], []
    return r


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


def w_extract_scan(row):
    ### tcp ###
    if "tcp" or "udp" in row:
        try:
            scan_df = extract_scan(row)
        except NoScanAvailable:
            row['host'] = 'down'
        return row


