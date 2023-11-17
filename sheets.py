import argparse
import pygsheets
import pandas as pd
import chardet
import traceback

# authorization
gc = pygsheets.authorize(service_file='creds.json')

def write_to_spreadsheet(file_name, spreadsheet_name, sheet_name, add_column_name=None, add_column_data=None, index=1, overwrite=False, append=False):
    print("file_name", file_name, "spreadsheet_name", spreadsheet_name, "sheet_name", sheet_name, "index", index, flush=True)

    try:
        # Detect the encoding of the file
        with open(file_name, 'rb') as f:
            result = chardet.detect(f.read())

        # Print the detected encoding
        print("Detected encoding:", result['encoding'])

        # Read the CSV file with the detected encoding
        data_frame = pd.read_csv(file_name, encoding=result['encoding'])
        if 'Percentage of Hit == True' in data_frame and 'Percentage of Hit == False' in data_frame:
            data_frame = data_frame.drop(columns=['Percentage of Hit == True', 'Percentage of Hit == False'])
        data_frame = data_frame.dropna(how='all')
        
        if 'Hit' in data_frame:
            first_column = data_frame.pop('Hit')
            data_frame.insert(0, 'Hit', first_column)
        if add_column_name and add_column_data:
            data_frame.insert(0, add_column_name, add_column_data)


        sh = gc.open(spreadsheet_name)

        existing_sheet = None

        try:
            # Check if the sheet with the same name already exists
            existing_sheet = sh.worksheet_by_title(sheet_name)
            print(sheet_name, "rows", existing_sheet.rows, flush=True)

            if append:
                # Append data to the existing sheet
                existing_data_frame = existing_sheet.get_as_df()
                if existing_sheet.rows == 0:
                    # If the sheet is empty, include the header
                    updated_data_frame = pd.concat([existing_data_frame, data_frame], ignore_index=True)
                    existing_sheet.set_dataframe(updated_data_frame, start=(1, 1), nan="", extend=True, copy_index=False, copy_head=False)
                else:
                    # If the sheet already has data, do not include the header
                    existing_sheet.set_dataframe(data_frame, start=(existing_sheet.rows + 1, 1), nan="", extend=True, copy_index=False, copy_head=False)
                print("Appended data to existing sheet:", sheet_name)
                return sh, existing_sheet

            elif overwrite:
                # Keep existing headers and formatting but replace all existing data
                # Clear the data range excluding headers
                existing_sheet.clear(start=(2, 1), end=(existing_sheet.rows + 1, existing_sheet.cols))
                # Set the new data
                existing_sheet.set_dataframe(data_frame, start=(2, 1), nan="", extend=True, copy_index=False, copy_head=False)
                print("Overwritten data in existing sheet:", sheet_name)
                return sh, existing_sheet

            else:
                raise ValueError("Sheet with the same name already exists. Use --overwrite or --append.")

        except pygsheets.exceptions.WorksheetNotFound:
            pass  # The sheet does not exist, proceed to create a new one

        new_sheet = sh.add_worksheet(sheet_name, index=index)
        new_sheet.set_dataframe(data_frame, (1, 1), nan="")
        print("Created new sheet:", sheet_name)
        return sh, new_sheet

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description='Write CSV file to Google Spreadsheet')
    parser.add_argument('--file_name', help='CSV file to be written to the spreadsheet')
    parser.add_argument('--spreadsheet_name', help='Name of the Google Spreadsheet')
    parser.add_argument('--sheet_name', help='Name of the sheet in the spreadsheet')
    parser.add_argument('--add_column_name', help='Name of the column to be added')
    parser.add_argument('--add_column_data', help='Data to be added in the new column')
    parser.add_argument('--index', type=int, default=1, help='Index of the new sheet (default is 1)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing sheet')
    parser.add_argument('--append', action='store_true', help='Append data to existing sheet')

    args = parser.parse_args()
    write_to_spreadsheet(args.file_name, args.spreadsheet_name, args.sheet_name, args.add_column_name, args.add_column_data, args.index, args.overwrite, args.append)

if __name__ == '__main__':
    main()
