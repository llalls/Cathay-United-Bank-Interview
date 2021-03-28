import pandas as pd


# check the number size of floor from chinese language
def total_floor_check(floor):
    standard = '十三'
    chinese_numbers = ['十', '一', '二', '三', '四', 
                         '五', '六', '七', '八', '九']
    floor = floor[:-1]
    if(len(floor) > len(standard)):
        return True
    elif(len(floor) == len(standard)):
        if(floor == standard):
            return True
        for i in range(len(floor)):
            floor_index = chinese_numbers.index(floor[i])
            standard_index = chinese_numbers.index(standard[i])
            if(floor_index > standard_index):
                return True
        return False
    else:
        return False




# read csv file
df_a = pd.read_csv('../real estate/a_lvr_land_a.csv')
df_b = pd.read_csv('../real estate/b_lvr_land_a.csv')
df_e = pd.read_csv('../real estate/e_lvr_land_a.csv')
df_f = pd.read_csv('../real estate/f_lvr_land_a.csv')
df_h = pd.read_csv('../real estate/h_lvr_land_a.csv')


# create dataframe
df_lists = [df_a, df_b, df_e, df_f, df_h] # all dataframe object
for i in df_lists:
    i.drop(0, axis=0, inplace=True) # remove english column row
df_all = pd.concat(df_lists, axis=0, ignore_index=True)


columns_name = []
for col in df_all.columns: 
    columns_name.append(col)
filter_a = pd.DataFrame(columns=columns_name)


total_nums = []         # 總件數
total_berths = []       # 總車位數
ave_price = []          # 平均總價元：總價元 / 總件數
ave_berthsPrice = []    # 平均車位總價元：車位總價元 / 總車位數


for index, row in df_all.iterrows():
    # filter_a
    if(isinstance(row[12], str) == True and '住家用' in row[12]):
        if(isinstance(row[11], str) == True and '住宅大樓' in row[11]):
            if(isinstance(row[10], str) == True and total_floor_check(row[10]) == True):
                filter_a = filter_a.append(row, ignore_index = True)
                print(filter_a.shape)
    
    # filter_b
    if(isinstance(row[8], str) == True and '土地' in row[8]):
        land = row[8].find('土地')
        building = row[8].find('建物')
        berth = row[8].find('車位')
        land_nums = int(row[8][land + 2 : building])
        building_nums = int(row[8][building + 2 : berth])
        berth_nums = int(row[8][berth + 2 : ])

        total_nums.append(land_nums + building_nums + berth_nums)
        total_berths.append(berth_nums)
        ave_price.append(int(int(row[21]) / (land_nums + building_nums + berth_nums)))
        if(berth_nums != 0):
            ave_berthsPrice.append(int(int(row[25]) / berth_nums))
        else:
            ave_berthsPrice.append(int(0))



df_all['總件數'] = total_nums
df_all['總車位數'] = total_berths
df_all['平均總價元'] = ave_price
df_all['平均車位總價元'] = ave_berthsPrice
filter_a.to_csv('filter_a.csv', encoding='utf_8_sig', index=False)
df_all.to_csv('filter_b.csv', encoding='utf_8_sig', index=False)