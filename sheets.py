import argparse
import pygsheets
import pandas as pd

# authorization
gc = pygsheets.authorize(service_file='creds.json')

def write_to_spreadsheet(file_name, spreadsheet_name, sheet_name, index=1, overwrite=True):
    print("file_name",file_name,"spreadsheet_name",spreadsheet_name,"sheet_name",sheet_name,"index",index)
    data_frame = pd.read_csv(file_name) 
    if 'Percentage of Hit == True' in data_frame and 'Percentage of Hit == False' in data_frame:
        data_frame = data_frame.drop(columns=['Percentage of Hit == True', 'Percentage of Hit == False'])
        
    if 'Hit' in data_frame:
        first_column = data_frame.pop('Hit') 
        data_frame.insert(0, 'Hit', first_column)
        
    data_frame = data_frame.dropna(how='all')
    sh = gc.open(spreadsheet_name)
    
    if overwrite:
        # Check if the sheet with the same name already exists
        try:
            existing_sheet = sh.worksheet_by_title(sheet_name)
            
            if existing_sheet:
                # Delete the existing sheet
                sh.del_worksheet(existing_sheet)
        except:
            print("Failed to overwrite, may not exist")
    
    new_sheet = sh.add_worksheet(sheet_name, index=index)
    new_sheet.set_dataframe(data_frame, (1, 1), nan="")
    return sh, new_sheet

def main():
    parser = argparse.ArgumentParser(description='Write CSV file to Google Spreadsheet')
    parser.add_argument('--file_name', help='CSV file to be written to the spreadsheet')
    parser.add_argument('--spreadsheet_name', help='Name of the Google Spreadsheet')
    parser.add_argument('--sheet_name', help='Name of the sheet in the spreadsheet')
    parser.add_argument('--index', type=int, default=1, help='Index of the new sheet (default is 1)')

    args = parser.parse_args()
    write_to_spreadsheet(args.file_name, args.spreadsheet_name, args.sheet_name, args.index)

if __name__ == '__main__':
    main()
