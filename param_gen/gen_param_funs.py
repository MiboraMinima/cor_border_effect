import os
import re

def populate_dict(dict_file, input_dir, output_dir, subdir, file, date):
    # Inputs
    input_path = f"'{input_dir}/{subdir}/{file}'"
    output_detail = f"{output_dir}/{subdir}/{subdir}_{date}_border_details"

    # Create the dir if it doesn't exist
    if not os.path.exists(output_detail):
        os.makedirs(output_detail)

    # Outputs
    output_dod_slope = f"{output_detail}/{subdir}_{date}_slope.tif"
    output_dod_dx = f"{output_detail}/{subdir}_{date}_slope_dx.tif"
    output_dod_dy = f"{output_detail}/{subdir}_{date}_slope_dy.tif"
    output_dod_dxx = f"{output_detail}/{subdir}_{date}_slope_dxx.tif"
    output_dod_dyy = f"{output_detail}/{subdir}_{date}_slope_dyy.tif"
    output_dod_dxy = f"{output_detail}/{subdir}_{date}_slope_dxy.tif"
    output_mask = f"{output_detail}/{subdir}_{date}_slope_mask.tif"
    output_dod_cleaned = f"{output_dir}/{subdir}/{subdir}_{date}_dod_cor_border.tif"

    # Fill the dictionary with paths
    dict_file['PARAMETERS']['INPUT'] = input_path
    dict_file['OUTPUTS']['OUTPUT_SLOPE'] = output_dod_slope
    dict_file['OUTPUTS']['OUTPUT_DX'] = output_dod_dx
    dict_file['OUTPUTS']['OUTPUT_DY'] = output_dod_dy
    dict_file['OUTPUTS']['OUTPUT_DXX'] = output_dod_dxx
    dict_file['OUTPUTS']['OUTPUT_DYY'] = output_dod_dyy
    dict_file['OUTPUTS']['OUTPUT_DXY'] = output_dod_dxy
    dict_file['OUTPUTS']['OUTPUT_MASK'] = output_mask
    dict_file['OUTPUTS']['OUTPUT_DOD'] = output_dod_cleaned

    return dict_file


def reset_dict():
    dict_file = {
        "PARAMETERS": {
            "INPUT": None
        },
        "OUTPUTS": {
            'OUTPUT_DX': None,
            'OUTPUT_DY': None,
            'OUTPUT_DXX': None,
            'OUTPUT_DYY': None,
            'OUTPUT_DXY': None,
            'OUTPUT_MASK': None,
            'OUTPUT_DOD': None
        }
    }

    return dict_file


def process_files(input_dir, output_dir, years, places):
    list_all = []
    for root, dirs, files in os.walk(input_dir):
        for subdir in dirs:
            if places and not years:
                if subdir in places:
                    print(subdir)
                    dict_file = reset_dict()
                    for file in os.listdir(f"{root}/{subdir}"):
                        print(file)
                        date = re.search(r'(\d{4}_\d{4})', file).group(1)
                        dict_res = populate_dict(dict_file, input_dir, output_dir, subdir, file, date)
                        list_all.append(dict_res)
                        dict_file = reset_dict()

            elif places and years:
                if subdir in places:
                    print(subdir)
                    dict_file = reset_dict()
                    for file in os.listdir(f"{root}/{subdir}"):
                        date = re.search(r'(\d{4}_\d{4})', file).group(1)
                        if date in years:
                            print(file)
                            dict_res = populate_dict(dict_file, input_dir, output_dir, subdir, file, date)
                            list_all.append(dict_res)
                            dict_file = reset_dict()
            elif not places and years:
                print(subdir)
                dict_file = reset_dict()
                for file in os.listdir(f"{root}/{subdir}"):
                    date = re.search(r'(\d{4}_\d{4})', file).group(1)
                    if date in years:
                        print(file)
                        dict_res = populate_dict(dict_file, input_dir, output_dir, subdir, file, date)
                        list_all.append(dict_res)
                        dict_file = reset_dict()
            else:
                print(subdir)
                dict_file = reset_dict()
                for file in os.listdir(f"{root}/{subdir}"):
                    print(file)
                    date = re.search(r'(\d{4}_\d{4})', file).group(1)
                    dict_res = populate_dict(dict_file, input_dir, output_dir, subdir, file, date)
                    list_all.append(dict_res)
                    dict_file = reset_dict()

    print(list_all)

    return list_all

