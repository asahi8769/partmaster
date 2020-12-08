words_not_to_skip = ['PAINT', 'DUST', 'SCR', 'MOLDING', 'FUNCTION', 'INJECTION', 'DM', '불량', 'HIGH EFFORT',
                     'COUPLING', 'MECHANISM', 'NOISE', 'PACKING', 'EXTRA', 'POSITION', 'WELD', 'PRESS', 'RUST',
                     'HOLE', 'PIN', 'NUT', 'LEVEL', 'LEATHER', 'STICKER', 'ID', 'WELDING', 'OPEN', 'FLUSH', 'CHARGING']

additional_exceptions = ['AA', 'AB', 'ACCORDING', 'ACID', 'ACTR', 'ACU', 'ACUTATOR', 'AFTER', 'XCIENT', 'KD', 'EHJ',
                         'ALSO', 'AN', 'ANTEENA', 'ANY', 'APPLICATION', 'AQL', 'ARE', 'AREA', 'ASAN', 'ASHA', 'ASSI',
                         'ASSY', 'AUTOGLASS', 'AUTOMOTIVE', 'AVAILABLE', 'BBD', 'BC', 'BDC', 'BDM', 'BE', 'BEFORE',
                         'BELT', 'BETWEEM', 'BETWEEN', 'BH', 'BJA', 'BJB', 'BJC', 'BMU', 'BOOSTER', 'BOTTOM', 'BQ',
                         'BRCT', 'BRD', 'BRK', 'BSA', 'BUTTONS', 'CA', 'CAME', 'CBR', 'CDC', 'CF', 'CHANG', 'QZC',
                         'CHEMICAL', 'CHNL', 'CHROME', 'CKLIP', 'CLEARLH', 'CLIPEND', 'CLOSING', 'CN', 'CNS', 'CO',
                         'COMBILAMP', 'COMES', 'COMING', 'COMPL', 'COMPLETE', 'CONCERN', 'CONNECTORS',
                         'CORPORATION', 'CRETA', 'CV', 'D&R', 'DAEDONG', 'DENSO', 'DH', 'DISCK', 'DKE', 'DL',
                         'DONG', 'DRRH', 'DUA', 'DUE', 'DURIGN', 'DURING', 'DY', 'ECOPLASTIC', 'ECOS', 'EK',
                         'ELEMENT', 'ENDPIECE', 'FB', 'FC', 'FE', 'FI', 'FOUND', 'FPSC', 'FR', 'FROM', 'FRT',
                         'FULLER', 'GCB', 'GCC', 'GCD', 'GCE', 'GCF', 'GE', 'GEARS', 'GI', 'GI', 'GIVING', 'GONG',
                         'GRL', 'GRUME', 'GSK', 'GSR', 'GX', 'HADS', 'HANKOOK', 'HAUSYS', 'HC', 'HCD', 'HCE', 'HCF',
                         'HCG', 'HCR', 'HDLLH', 'HE', 'HEADLAMP', 'HEADLH', 'HEADRH', 'HEE', 'HEMMING', 'HENKEL',
                         'HEUNG', 'HI', 'HING', 'HM', 'HMI', 'HMMC', 'HMSK', 'HOME', 'HTK', 'HX', 'HYUNDAI', 'IL',
                         'ILLUMINATION', 'IMT', 'INCOMING', 'IND', 'INDIA', 'INFAC', 'INFORMATION',
                         'INITIAL', 'INSPECTOR', 'INTERMOBILE', 'INTERNAL', 'IQR', 'IS', 'ISIR', 'ISSUE', 'ISSUES',
                         'IT', 'ITS', 'JIG', 'JIN', 'JNT', 'JOIL', 'JS', 'JULY', 'JUNG', 'JUST', 'KA', 'KAC', 'KF',
                         'KIA', 'KIMCHEON', 'KMS', 'KNIFE', 'KNOBB', 'KOMOS', 'KOREA', 'KWANGJIN', 'KYUNG', 'LANE',
                         'LEFT', 'LG', 'LH', 'LHD', 'LINKAGE', 'LIQUID', 'LN', 'LOADING', 'LOT', 'LOUD', 'LPL',
                         'LS', 'LTD', 'LUG', 'MANDO', 'MDPS', 'METAL', 'MJ', 'MOBIS', 'MODEL', 'MONETARY', 'MTGRH',
                         'MU', 'MULTIPLE', 'NAIL', 'NAJEON', 'NATIONAL', 'NEW', 'NG', 'NO.', 'NOIDA', 'NOTCH', 'NVH',
                         'OB', 'OBSERVED', 'OCCURRED', 'OF', 'OFFSET', 'OK', 'OPERATING', 'OPERATOR',
                         'PACKED', 'PADDLE', 'PBBLE', 'PCB', 'PCD', 'PCM', 'PDI', 'PHEV', 'PLAKOR', 'PLATECH',
                         'POONGSUNG', 'PP', 'PPR', 'PRESENTED', 'PRIVATE', 'PROTECTION', 'PRTN', 'PSTN',
                         'PTRH', 'PVT', 'PYUNG', 'QARTER', 'QB', 'QC', 'QRT', 'QUALITY', 'QXI', 'RATTLE', 'REAR',
                         'REFER', 'REISSUE', 'RELATED', 'REPAIR', 'OI', '로', 'QI', 'FOR', 'NTF', 'SIG', '돌때', '매우',
                         'REWORK', 'RH', 'RIB', 'ROCS', 'ROOFLH', 'RP', 'RR', 'RRDR', 'RRRH', 'RT', 'QF', 'ACA',
                         'RU', 'SAE', 'SAEDONG', 'SAMBOA', 'SAMBOPLATEC', 'SAME', 'SAMPLE', 'SAMSHIN', 'SAMSONG',
                         'SAN', 'SB', 'SC', 'SEAR', 'SEATBELT', 'SEATING', 'SECOND', 'SEEM', 'SENDER', 'SEOYON',
                         'SEQUENCING', 'SEUN', 'SHIN', 'SHINKI', 'SHLD', 'SHOWING', 'SIDELH', 'SL',
                         'SLH', 'SORTED', 'SOS', 'SPOOL', 'SQUEAK', 'SRH', 'SSUNGLASS', 'STAGE', 'STD', 'STICK',
                         'STUDBOLT', 'SUBCONTRACT', 'SUNG', 'SUNGLASS', 'SUNGLASSED', 'SUNGLASSES',
                         'SUPPLIER', 'SUV', 'SVG', 'TACHOMETER', 'TAE', 'TCU', 'TECH', 'TENSR', 'TF',
                         'THAN', 'THE', 'THERE', 'THORTTLE', 'TL', 'TLI', 'TMA', 'KWANGIL', 'INNOVATION', 'UMA',
                         'TOO', 'TR', 'TRANIT', 'TRANS', 'TRANSYS', 'TRG', 'TRIGO', 'TRW', 'TTX', 'TURNS', 'UI',
                         'UIP', 'UNIV', 'UNUSED', 'USED', 'VER', 'VIBRACOUSTIC', 'VISIBLE', 'VISUAL', 'VS', 'WAS',
                         'WEBASTO', 'WHEN', 'WHILE', 'WHISTLE', 'WI', 'WIA', 'WILL', 'WIRRING', 'WON', 'WOO',
                         'YOUNGSAN', 'YPI', 'YZ', 'КК''나전', '도어벨트', '만도', '스트라이커외', '오송', '으로', '인한',
                         'COMPRESSION', 'MTNG', 'BORE', 'VR', 'HOT', 'STAPLE', 'BULB', 'SEJIN', 'DELTARH', 'DRLH',
                         'JO', 'KMI', 'ACN', 'SAMBO', 'ILJIN', 'HLLD', 'JOYSON', 'SYSTEMS', 'YP', 'REPORT', 'QL',
                         'GAT', 'HCC', 'POLYURETHANE', 'CHE', 'JF', 'КК', 'WERE', 'REJECTED', 'FIT', 'LK', 'TOTE',
                         'NIL', '방안협의', 'ROFO', 'FRLH', 'GLA', 'CHB', 'OTRRH', 'LIFTGATE', 'BTZ', 'INVESTIGATION',
                         '업체사전신고', '클린포인트', 'VP', 'SX', 'DF', 'RB', 'PN', 'DN', 'PS', 'FM', 'AM', 'GR', 'NA',
                         'SA', 'MT', 'OR', 'VN', 'CH', 'OD', 'EL', 'PL', 'HO', 'MV', 'DP', 'TC', 'YU', 'LX', '조치',
                         'EO', 'DM', 'YB', 'SQ', 'ID', 'PA', 'BB', 'AHV', 'ANC', 'ASM', 'ASS', 'AWK', 'BAK',
                         'BCB', 'BCC', 'BIG', 'BPP', 'BRE', 'BRF', 'BUT', 'CHA', 'CHC', 'CHD', 'CHK', 'CRB', 'CRK',
                         'DEC', 'DIM', 'DLC', 'DTC', 'ESA', 'ESC', 'ETR', 'EVA', 'EXA', 'FEW', 'FGG', 'GAH', 'GRU',
                         'HAD', 'HCB', 'IGN', 'INA', 'INB', 'ITW', 'KPS', 'KUM', 'LIQ', 'MIS', 'MIX', 'MRG', 'MUA',
                         'NCM', 'ODO', 'OLL', 'ONE', 'OPN', 'PCS', 'PEW', 'PHO', 'PIN', 'VPC',
                         'RED', 'RIO', 'ROM', 'SDE', 'SHF', 'SUC', 'TPO', 'UQA', 'VIN', 'WCA', 'YDM', 'ASSR', 'ASST',
                         'BEEN', 'BOTH', 'BUMP', 'CASS', 'CIMB', 'CTPA', 'DOME', 'TLID', 'DTCP', 'EMBO', 'FIAL', 'HAVE',
                         'INFO','JBOX', 'KDQR', 'KMMG','LOT성','MUCH', 'NCAP', 'NICK','RRLH','THIS', 'TITL','WEBB',
                         'WHLD', 'WORK', 'WRMG', '弧度不良', '焊点分离', 'SEUNG', 'GUMMCHANG', 'SEWON' ,'FOOSUNG', '인판넬',
                         ]
